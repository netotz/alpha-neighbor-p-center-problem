namespace Anpcp.Core.Heuristics;

/// <summary>
/// Heuristic algorithm contract.
/// </summary>
public interface IHeuristic
{
    /// <summary>
    /// Problem parameter <c>p</c>, size of a solution <c>S</c>.
    /// <c>p = |S|</c>
    /// </summary>
    int PSize { get; }
    Instance Instance { get; }
    /// <summary>
    /// Seed for random generators. If <c>null</c>, a random one is used.
    /// </summary>
    int? Seed { get; }
}
