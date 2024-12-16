using System.Collections.Immutable;

using Anpcp.Core.Heuristics.LocalSearches.Afvs;
using Anpcp.Core.Wrappers;

namespace Anpcp.Core.UnitTests.Heuristics.LocalSearches.Afvs;

public class AlphaNeighborhoodTests
{
    public static ImmutableHashSet<int> FakeUserIds { get; } = [0];
    public static HashSet<int> FakeCenterIds { get; } = [0, 1, 2];
    public static IdIndexMap FakeIdIndexMap { get; } = new(
        FakeUserIds.ToDictionary(u => u, u => u),
        FakeCenterIds.ToDictionary(c => c, c => c));

    public static object[][] CommonInput { get; } = [
        [
            2, 0, 1,
            FakeCenterIds,
            FakeUserIds,
            new Allocator(2, 1, 3, FakeIdIndexMap),
            new DistancesMatrix(
                [new(0, 0, 0)],
                [new(0, 0, 1), new(1, 0, 2), new(2, 0, 3)]),
        ],
    ];

    public static object[][] ConstructorData { get; } = [
        [
            ..CommonInput[0],
            1, 2, 3,
        ],
    ];

    [Theory]
    [MemberData(nameof(ConstructorData))]
    public void Constructor_CorrectlyConstructsAllocations(
        int fakeAlpha, int fakeUserId, int fakeFiDistance,
        HashSet<int> fakeCenterIds,
        ImmutableHashSet<int> fakeUserIds,
        Allocator fakeAllocator,
        DistancesMatrix fakeDistancesUF,
        int expectedAlphaMinusOneDistance,
        int expectedAlphaDistance,
        int expectedAlphaPlusOneDistance)
    {
        fakeAllocator.AllocateAll(
            fakeUserIds,
            fakeDistancesUF.GetNextNearestFacility,
            fakeCenterIds);

        var mockAlphaNeighborhood = new AlphaNeighborhood(
            fakeAlpha, fakeUserId, fakeFiDistance,
            in fakeCenterIds,
            in fakeAllocator,
            in fakeDistancesUF);

        Assert.Equal(expectedAlphaMinusOneDistance, mockAlphaNeighborhood.AlphaMinusOneDistance);
        Assert.Equal(expectedAlphaDistance, mockAlphaNeighborhood.AlphaDistance);
        Assert.Equal(expectedAlphaPlusOneDistance, mockAlphaNeighborhood.AlphaPlusOneDistance);
    }

    public static object[][] UpdatingIdsData { get; } = [
        [
            ..CommonInput[0],
            new [] { 0 },
        ],
    ];

    [Theory]
    [MemberData(nameof(UpdatingIdsData))]
    public void GetUpdatingIdsData_ReturnsCorrectIds(
        int fakeAlpha, int fakeUserId, int fakeFiDistance,
        HashSet<int> fakeCenterIds,
        ImmutableHashSet<int> fakeUserIds,
        Allocator fakeAllocator,
        DistancesMatrix fakeDistancesUF,
        IEnumerable<int> expectedIds)
    {
        fakeAllocator.AllocateAll(
            fakeUserIds,
            fakeDistancesUF.GetNextNearestFacility,
            fakeCenterIds);

        var stubAlphaNeighborhood = new AlphaNeighborhood(
            fakeAlpha, fakeUserId, fakeFiDistance,
            in fakeCenterIds,
            in fakeAllocator,
            in fakeDistancesUF);

        var actualIds = stubAlphaNeighborhood.GetUpdatingIds();

        Assert.Equal(expectedIds, actualIds);
    }
}
