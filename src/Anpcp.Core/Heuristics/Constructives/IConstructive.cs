namespace Anpcp.Core.Heuristics.Constructives;

/// <summary>
/// Constructive heuristic contract.
/// </summary>
public interface IConstructive<TInstance, TSolution> : IHeuristic<TInstance>
    where TInstance : BaseInstance
    where TSolution : BaseSolution<TInstance>
{
    TSolution Construct();
}
