namespace Anpcp.Core.Heuristics.Constructives;

/// <summary>
/// Constructive heuristic contract.
/// </summary>
public interface IConstructive : IHeuristic
{
    Solution Construct();
}
