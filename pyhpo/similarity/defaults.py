import math
from typing import List

from pyhpo.similarity.base import SimilarityBase
import pyhpo


class Resnik(SimilarityBase):
    """
    Based on *Resnik P, Proceedings of the 14th IJCAI, (1995)*

    https://www.ijcai.org/Proceedings/95-1/Papers/059.pdf
    """

    def __call__(
        self,
        term1: "pyhpo.HPOTerm",
        term2: "pyhpo.HPOTerm",
        kind: str,
        dependencies: List[float],
    ) -> float:
        sim = 0.0
        for term in term1.common_ancestors(term2):
            ic = term.information_content[kind]
            if ic > sim:
                sim = ic

        return sim


class Lin(SimilarityBase):
    """
    Based on *Lin D, Proceedings of the 15th ICML, (1998)*

    https://dl.acm.org/doi/10.5555/645527.657297
    """

    dependencies: List[str] = ["resnik"]

    def __call__(
        self,
        term1: "pyhpo.HPOTerm",
        term2: "pyhpo.HPOTerm",
        kind: str,
        dependencies: List[float],
    ) -> float:
        ic_t1 = term1.information_content[kind]
        ic_t2 = term2.information_content[kind]
        try:
            return (2 * dependencies[0]) / (ic_t1 + ic_t2)
        except ZeroDivisionError:
            return 0.0


class JC(SimilarityBase):
    """
    Jiang & Conrath similarity Score, based on
    *Jiang J, Conrath D, Rocling X, (1997) and
    Deng Y, et. al., PLoS One, (2015)*

    https://aclanthology.org/O97-1002.pdf

    .. note::

        This method was previously wrongly implemented
        and fixed in 3.3.0 based on `this discussion <https://github.com/anergictcell/pyhpo/issues/20>`_

    """

    dependencies: List[str] = ["resnik"]

    def __call__(
        self,
        term1: "pyhpo.HPOTerm",
        term2: "pyhpo.HPOTerm",
        kind: str,
        dependencies: List[float],
    ) -> float:
        if term1 == term2:
            return 1.0

        ic_t1 = term1.information_content[kind]
        ic_t2 = term2.information_content[kind]

        if ic_t1 == 0.0 or ic_t2 == 0.0:
            return 0.0

        return 1.0 / (ic_t1 + ic_t2 - (2.0 * dependencies[0]) + 1.0)


class Relevance(SimilarityBase):
    """
    Based on *Schlicker A, et.al., BMC Bioinformatics, (2006)*

    https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-7-302
    """

    dependencies: List[str] = ["resnik", "lin"]

    def __call__(
        self,
        term1: "pyhpo.HPOTerm",
        term2: "pyhpo.HPOTerm",
        kind: str,
        dependencies: List[float],
    ) -> float:
        return dependencies[1] * (1 - (math.exp(dependencies[0] * -1)))


class InformationCoefficient(SimilarityBase):
    """
    Based on *Li B, et. al., arXiv, (2010)*

    https://arxiv.org/abs/1001.0958
    """

    dependencies: List[str] = ["resnik", "lin"]

    def __call__(
        self,
        term1: "pyhpo.HPOTerm",
        term2: "pyhpo.HPOTerm",
        kind: str,
        dependencies: List[float],
    ) -> float:
        return dependencies[1] * (1 - (1 / (1 + dependencies[0])))


class GraphIC(SimilarityBase):
    """
    Graph based Information coefficient, based on
    *Deng Y, et. al., PLoS One, (2015)*

    https://pubmed.ncbi.nlm.nih.gov/25664462/
    """

    def __call__(
        self,
        term1: "pyhpo.HPOTerm",
        term2: "pyhpo.HPOTerm",
        kind: str,
        dependencies: List[float],
    ) -> float:
        if term1 == term2:
            return 1.0

        common = sum(
            [x.information_content[kind] for x in term1.common_ancestors(term2)]
        )
        union = sum(
            [
                x.information_content[kind]
                for x in (term1.all_parents | term2.all_parents)
            ]
        )

        try:
            return common / union
        except ZeroDivisionError:
            return 0.0


class Distance(SimilarityBase):
    """
    actual distance (number of hpos) between Terms
    """

    def __call__(
        self,
        term1: "pyhpo.HPOTerm",
        term2: "pyhpo.HPOTerm",
        kind: str,
        dependencies: List[float],
    ) -> float:
        try:
            dist = term1.path_to_other(term2)[0]
        except IndexError:
            # No path found -> This can only happen if one of the
            # terms is obsolete or otherwise not part of the Ontology
            return 0.0

        return 1 / (dist + 1)


def register_defaults(simscore: "pyhpo.similarity.base._Similarity") -> None:
    simscore.register("resnik", Resnik)
    simscore.register("lin", Lin)
    simscore.register("jc", JC)
    simscore.register("jc2", JC)
    simscore.register("rel", Relevance)
    simscore.register("ic", InformationCoefficient)
    simscore.register("graphic", GraphIC)
    simscore.register("dist", Distance)
