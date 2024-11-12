using System.Collections.Immutable;

using Anpcp.Core.Solutions.Models;

namespace Anpcp.Core.Solutions;

public class AnpcpSolution : BaseSolution
{
    /// <summary>
    /// <inheritdoc/>
    /// </summary>
    public AnpcpSolution(HashSet<int> allFacilities) : base(allFacilities) { }

    /// <summary>
    /// <inheritdoc/>
    /// </summary>
    public AnpcpSolution(
        HashSet<int> closedFacilities,
        HashSet<int> openFacilities,
        Allocation criticalAllocation)
        : base(closedFacilities, openFacilities, criticalAllocation) { }

    /// <summary>
    /// <inheritdoc/>
    /// </summary>
    public AnpcpSolution(AnpcpSolution originalSolution) : base(originalSolution) { }

    /// <remarks>Time O(np)</remarks>
    public void UpdateCriticalAllocation(
        ImmutableHashSet<int> userIds,
        Func<int, Allocation> alphathNearestGetter)
    {
        //// O(np)
        // O(n)
        CriticalAllocation = userIds
            // O(p)
            .Select(alphathNearestGetter)
            .MaxBy(a => a.Distance)!;
    }
}
