using Anpcp.Core.Heuristics.Constructives.Rgd;
using Anpcp.Core.Heuristics.LocalSearches.Afvs;
using Anpcp.Core.Instances;

namespace Anpcp.Core.Heuristics.Metaheuristics;

public class GraspRgdAfvs(
    int maxIterations,
    TimeSpan timeLimit,
    RandomizedGreedyDispersion<InstanceTwoSets> constructive,
    AlphaFastVertexSubstitution localSearch)
    : BaseGrasp<
        InstanceTwoSets,
        RandomizedGreedyDispersion<InstanceTwoSets>,
        AlphaFastVertexSubstitution>(maxIterations, timeLimit, constructive, localSearch)
{

}
