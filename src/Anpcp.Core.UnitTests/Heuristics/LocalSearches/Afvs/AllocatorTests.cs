using System.Collections.Immutable;

using Anpcp.Core.Heuristics.LocalSearches.Afvs;

namespace Anpcp.Core.UnitTests.Heuristics.LocalSearches.Afvs;

public class AllocatorTests
{
    public static object[][] Data { get; } = [
        [
            2, 2, 2,
            Enumerable.Range(0, 2).ToImmutableHashSet(),
            (int u) => Enumerable.Range(0, 2),
            new HashSet<int>(),
            // no centers, all allocations should = 0
            new int[,] {
                { 0, 0 },
                { 0, 0 },
            }
        ],
        [
            2, 2, 3,
            Enumerable.Range(0, 2).ToImmutableHashSet(),
            (int u) => Enumerable.Range(0, 3),
            // only facilities 0, 1 are centers
            Enumerable.Range(0, 2).ToHashSet(),
            new int[,] {
                { 1, 2, 0 },
                { 1, 2, 0 },
            }
        ],
        [
            2, 3, 4,
            Enumerable.Range(0, 3).ToImmutableHashSet(),
            // arbitrary "nearest" facilities
            (int u) => u switch {
                0 => new []{ 0, 1, 2, 3 },
                1 => [3, 2, 1, 0],
                2 => [0, 2, 1, 3],
                _ => []
            },
            Enumerable.Range(0, 3).ToHashSet(),
            new int[,] {
                { 1, 2, 3, 0 },
                { 3, 2, 1, 0 },
                { 1, 3, 2, 0 }
            }
        ],
    ];

    [Theory]
    [MemberData(nameof(Data))]
    public void AllocateAll_CorrectlyFillsAllocationsMatrix(
        int alpha, int n, int m,
        ImmutableHashSet<int> fakeUserIds,
        Func<int, IEnumerable<int>> fakeNearestFacilitiesGetter,
        HashSet<int> fakeCenters,
        int[,] expectedAllocationsMatrix)
    {
        var mockAllocator = new Allocator(alpha, n, m);

        mockAllocator.AllocateAll(fakeUserIds, fakeNearestFacilitiesGetter, fakeCenters);

        for (var i = 0; i < n; i++)
        {
            for (var j = 0; j < m; j++)
            {
                Assert.True(expectedAllocationsMatrix[i, j] == mockAllocator[i, j]);
            }
        }
    }
}
