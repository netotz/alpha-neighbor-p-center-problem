using Anpcp.Core.Heuristics.Constructives;
using Anpcp.Core.Instances;

namespace Anpcp.Core.UnitTests.Heuristics.Constructives;

/// <summary>
/// Tests of constructive heuristics that solve the PDP:
/// <see cref="FastGreedyDispersion"/> and <see cref="OriginalGreedyDispersion"/>.
/// </summary>
public class PdpConstructiveTests
{
    public static int? TestSeed => 20240402;
    public static InstanceSameSet SeededInstanceSameSet_m5 { get; } = new(5, 100, 100, TestSeed);
    public static InstanceSameSet SeededInstanceSameSet_m10 { get; } = new(10, 100, 100, TestSeed);
    public static InstanceSameSet SeededInstanceSameSet_m50 { get; } = new(50, seed: TestSeed);
    public static InstanceTwoSets SeededInstanceTwoSets_m5 { get; } = new(1, 5, 100, 100, TestSeed);
    public static InstanceTwoSets SeededInstanceTwoSets_m10 { get; } = new(1, 10, 100, 100, TestSeed);
    public static InstanceTwoSets SeededInstanceTwoSets_m50 { get; } = new(1, 50, seed: TestSeed);

    public static object[][] Data { get; } = [
        [SeededInstanceSameSet_m5, 2, 3],
        [SeededInstanceSameSet_m5, 4, 1],
        [SeededInstanceSameSet_m10, 2, 8],
        [SeededInstanceSameSet_m10, 5, 5],
        [SeededInstanceSameSet_m10, 9, 1],
        [SeededInstanceSameSet_m50, 5, 45],
        [SeededInstanceSameSet_m50, 10, 40],
        [SeededInstanceSameSet_m50, 20, 30],
        [SeededInstanceSameSet_m50, 40, 10],

        [SeededInstanceTwoSets_m5, 2, 3],
        [SeededInstanceTwoSets_m5, 4, 1],
        [SeededInstanceTwoSets_m10, 2, 8],
        [SeededInstanceTwoSets_m10, 5, 5],
        [SeededInstanceTwoSets_m10, 9, 1],
        [SeededInstanceTwoSets_m50, 5, 45],
        [SeededInstanceTwoSets_m50, 10, 40],
        [SeededInstanceTwoSets_m50, 20, 30],
        [SeededInstanceTwoSets_m50, 40, 10],
    ];

    /// <summary>
    /// Both heuristics should return the same solution:
    /// same set of open facilities and same objective function value.
    /// </summary>
    [Theory]
    [MemberData(nameof(Data))]
    public void Construct_ReturnsSameSolution<TInstance>(
        TInstance instance,
        int p,
        int expectedCloseds)
            where TInstance : BaseInstance
    {
        var stubOgd = new OriginalGreedyDispersion<TInstance>(instance, p, TestSeed);
        var stubFgd = new FastGreedyDispersion<TInstance>(instance, p, TestSeed);

        var mockOgdSolution = stubOgd.Construct();
        mockOgdSolution.UpdateCriticalAllocation(instance.DistancesFF);

        var mockFgdSolution = stubFgd.Construct();

        Assert.Equal(mockOgdSolution.Centers, mockFgdSolution.Centers);

        Assert.Equal(mockOgdSolution.ObjectiveFunctionValue, mockFgdSolution.ObjectiveFunctionValue);

        Assert.Equal(expectedCloseds, mockOgdSolution.ClosedFacilities.Count);
        Assert.Equal(expectedCloseds, mockFgdSolution.ClosedFacilities.Count);
    }
}
