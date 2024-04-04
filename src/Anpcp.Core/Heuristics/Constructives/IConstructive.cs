namespace Anpcp.Core.Heuristics.Constructives;

/// <summary>
/// Constructive heuristic contract.
/// </summary>
public interface IConstructive<TSolution> : IHeuristic
    where TSolution : BaseSolution
{
    TSolution Construct();
}
