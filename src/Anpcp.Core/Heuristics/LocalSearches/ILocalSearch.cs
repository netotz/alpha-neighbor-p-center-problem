using Anpcp.Core.Instances;
using Anpcp.Core.Solutions;

namespace Anpcp.Core.Heuristics.LocalSearches;

public interface ILocalSearch<TInstance, TSolution> : IHeuristic<TInstance>
    where TInstance : BaseInstance
    where TSolution : BaseSolution
{
    TSolution Solution { get; }

    TSolution Improve();
}
