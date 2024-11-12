using System.Collections.Immutable;

using Anpcp.Core.Solutions;
using Anpcp.Core.Solutions.Models;

namespace Anpcp.Core.UnitTests.Solutions;

public class AnpcpSolutionTests
{
    public static object[][] Data { get; } = [
        [
            new HashSet<int> { 0 },
            ImmutableHashSet.Create(0),
            (int u) => new Allocation(0, 0, 0),
            new Allocation(0, 0, 0),
        ],
        [
            new HashSet<int> { 0, 1 },
            ImmutableHashSet.Create(0, 1),
            // arbitrary alpha-centers
            (int u) => u switch {
                0 => new Allocation(u, 1, 10),
                1 => new Allocation(u, 1, 20),
                _ => null
            },
            new Allocation(1, 1, 20),
        ],
        [
            new HashSet<int> { 0, 1, 2 },
            ImmutableHashSet.Create(0, 1, 2),
            (int u) => u switch {
                0 => new Allocation(u, 2, 20),
                1 => new Allocation(u, 1, 10),
                2 => new Allocation(u, 0, 30),
                _ => null
            },
            new Allocation(2, 0, 30),
        ],
    ];

    [Theory]
    [MemberData(nameof(Data))]
    public void UpdateCriticalAllocation_CorrectlyUpdatesIt(
        HashSet<int> fakeFacilityIds,
        ImmutableHashSet<int> fakeUserIds,
        Func<int, Allocation> fakeAlphathNearestGetter,
        Allocation expectedCriticalAllocation)
    {
        var mockSolution = new AnpcpSolution(fakeFacilityIds);

        mockSolution.UpdateCriticalAllocation(fakeUserIds, fakeAlphathNearestGetter);
        var actualCriticalAllocation = mockSolution.CriticalAllocation;

        Assert.Equal(expectedCriticalAllocation, actualCriticalAllocation);
    }
}
