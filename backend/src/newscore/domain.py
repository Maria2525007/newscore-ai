"""Query domain filter — pre-check перед RSS-fetch.

Если запрос не относится к тематике источников (бизнес, финансы, экономика,
политика) — возвращает False до любых сетевых вызовов. Экономит 2-5 сек
RSS-fetch; при горячей e5-base добавляет ~30-50 мс.

Принцип: вычисляем max cosine между query и набором ~20 типичных заголовков
из наших источников. Если max_sim < threshold → запрос не про нашу тематику.

Калибровка (intfloat/multilingual-e5-base):
  - Релевантные запросы («курс доллара», «инфляция»): max_sim 0.79–0.84
  - Нерелевантные («антибиотики», «квантовая физика»): max_sim 0.74–0.77
  - Граница: 0.775 (зазор ~0.016 от ближайшего релевантного)
"""

from __future__ import annotations

import numpy as np
import structlog

from newscore.embeddings import get_st_model

log = structlog.get_logger(__name__)

_MODEL_NAME = "intfloat/multilingual-e5-base"

# Типичные заголовки из наших источников (RBC, Коммерсант, Ведомости,
# Интерфакс, Forbes RU). Отражают реальный тематический охват корпуса.
# Embeddings вычисляются один раз при первом обращении.
_SAMPLE_CORPUS: list[str] = [
    "Центральный банк повысил ключевую ставку до рекордного уровня",
    "Курс доллара достиг максимума за два года на торгах Московской биржи",
    "Нефть марки Brent торгуется вблизи 70 долларов за баррель",
    "Акции Сбербанка выросли после публикации квартальной отчётности",
    "Инфляция в России ускорилась по итогам прошедшего месяца",
    "Минфин разместил ОФЗ на десятки миллиардов рублей",
    "Российские компании увеличили экспорт в страны БРИКС",
    "Санкции ограничили доступ к западным технологиям для ряда отраслей",
    "ВВП России вырос в первом квартале текущего года",
    "Крупная розничная сеть открыла новые магазины в регионах",
    "Ипотечные ставки снизились впервые за несколько месяцев",
    "Стоимость металлов на мировых рынках снизилась из-за замедления спроса",
    "Прибыль нефтяных компаний выросла на фоне роста цен на сырьё",
    "Малый бизнес получит налоговые льготы на ближайшие годы",
    "Торговый оборот между Россией и Китаем превысил исторический максимум",
    "Правительство увеличило расходы бюджета на инфраструктурные проекты",
    "Банк России ввёл ограничения на операции с иностранной валютой",
    "Сделка по слиянию двух крупных компаний одобрена антимонопольной службой",
    "Рублёвые вклады принесли вкладчикам высокую доходность в текущем году",
    "Экспортная пошлина на зерно изменена с начала нового квартала",
]

# Corpus embeddings вычисляются один раз и живут всё время процесса.
_corpus_embs: np.ndarray | None = None


def _get_corpus_embs() -> np.ndarray:
    global _corpus_embs
    if _corpus_embs is None:
        model = get_st_model(_MODEL_NAME)
        _corpus_embs = np.asarray(
            model.encode(
                [f"passage: {t}" for t in _SAMPLE_CORPUS],
                normalize_embeddings=True,
                show_progress_bar=False,
                batch_size=16,
            ),
            dtype=np.float32,
        )
    return _corpus_embs


class DomainChecker:
    """Проверяет, что запрос относится к тематике источников.

    Использует тот же e5-base синглтон что EmbeddingMatcher — двойной загрузки нет.
    При горячей модели: ~30-50 мс на запрос.

    Критерии откалиброваны на реальных заголовках из источников:
      threshold=0.775: релевантные дают max_sim 0.79-0.85, нерелевантные 0.74-0.77.
      min_spread=0.018: нерелевантные дают равномерно низкие sim по всему corpus
      (spread 0.008-0.017), тогда как релевантные «цепляются» за ближайший
      заголовок (spread 0.030-0.094).
    """

    def __init__(
        self,
        threshold: float = 0.775,
        min_spread: float = 0.018,
        model_name: str = _MODEL_NAME,
    ) -> None:
        self.threshold = threshold
        self.min_spread = min_spread
        self.model_name = model_name

    def is_relevant(self, query: str) -> tuple[bool, float]:
        """Возвращает (relevant, max_sim_score).

        relevant=True  → пайплайн продолжается (fetch + match).
        relevant=False → оркестратор возвращает no_relevant_matches без fetch.

        Критерий (оба условия должны выполняться):
          1. max_sim >= threshold     — хотя бы один заголовок в corpus близок
          2. spread >= min_spread     — query специфична к тематике, а не равномерно
                                       далека от всего (spread = max - mean по corpus)
        """
        model = get_st_model(self.model_name)
        q_emb = model.encode(
            [f"query: {query}"],
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]
        corpus_embs = _get_corpus_embs()
        sims = corpus_embs @ np.asarray(q_emb, dtype=np.float32)
        max_sim = float(sims.max())
        spread = float(max_sim - sims.mean())
        relevant = max_sim >= self.threshold and spread >= self.min_spread
        log.debug(
            "domain_check",
            query=query[:80],
            max_sim=round(max_sim, 4),
            spread=round(spread, 4),
            relevant=relevant,
            threshold=self.threshold,
            min_spread=self.min_spread,
        )
        return relevant, max_sim
