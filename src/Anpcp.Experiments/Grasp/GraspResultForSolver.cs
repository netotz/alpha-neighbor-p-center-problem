namespace Anpcp.Experiments.Grasp;

internal record GraspResultForSolver
{
    internal string TspInstanceName { get; init; } = "";
    /// <summary>
    /// Number of total nodes (1 set) or users (2 sets)
    /// </summary>
    internal int N { get; init; }
    /// <summary>
    /// Number of facilities (2 sets)
    /// </summary>
    internal int? M { get; init; }
    /// <summary>
    /// Index of instance variation (2 sets)
    /// </summary>
    internal string? Index { get; init; }
    internal int PValue { get; init; }
    internal int Alpha { get; init; }
    internal int ObjectiveFunctionValue { get; init; }
    internal IEnumerable<int> CenterIds { get; init; } = [];
    internal IEnumerable<(int, int, int)> Assignments { get; init; } = [];
}
