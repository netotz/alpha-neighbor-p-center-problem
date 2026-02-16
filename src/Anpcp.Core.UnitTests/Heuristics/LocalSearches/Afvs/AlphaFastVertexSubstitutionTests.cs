using Anpcp.Core.Heuristics.LocalSearches.Afvs;
using Anpcp.Core.Instances;
using Anpcp.Core.Solutions;
using Anpcp.Core.Solutions.Models;

namespace Anpcp.Core.UnitTests.Heuristics.LocalSearches.Afvs;

public class AlphaFastVertexSubstitutionTests
{
    public static int TestSeed => 0;
    public static InstanceTwoSets DummyInstanceTwoSets { get; } = new(1, 1, seed: TestSeed);
    public static AnpcpSolution EmptySolution { get; } = new([]);
    public static object[][] ExceptionData { get; } = [
        // a == p
        [2, 2, DummyInstanceTwoSets, EmptySolution],
        // a > p
        [2, 3, DummyInstanceTwoSets, EmptySolution],
    ];

    [Theory]
    [MemberData(nameof(ExceptionData))]
    public void Constructor_ThrowsArgumentException(
        int p, int alpha,
        InstanceTwoSets dummyInstance,
        AnpcpSolution emptySolution)
    {
        Assert.Throws<ArgumentException>(()
            => new AlphaFastVertexSubstitution<InstanceTwoSets>(
                dummyInstance,
                p, alpha,
                emptySolution,
                TestSeed));
    }

    public static object[][] TwoSets_ImprovableData { get; } = [
        [
            // p = 3, a = 2
            3, 2,
            new InstanceTwoSets(PathHelper.GetAbsolute(@"Data\fake8_4_4.anpcp.tsp")),
            new AnpcpSolution([5], [6, 7, 8], new Allocation(4, 7, 36)),
            new AnpcpSolution([7], [5, 6, 8], new Allocation(4, 6, 28))
        ],
        [
            3, 2,
            new InstanceTwoSets(PathHelper.GetAbsolute(@"Data\fake9_4_5.anpcp.tsp")),
            new AnpcpSolution([5, 6], [7, 8, 9], new Allocation(4, 8, 53)),
            new AnpcpSolution([7, 8], [5, 6, 9], new Allocation(4, 6, 28))
        ],
        [
            4, 3,
            new InstanceTwoSets(PathHelper.GetAbsolute(@"Data\fake9_4_5.anpcp.tsp")),
            new AnpcpSolution([5], [6, 7, 8, 9], new Allocation(4, 8, 53)),
            new AnpcpSolution([8], [5, 6, 7, 9], new Allocation(4, 7, 36))
        ],
    ];

    [Theory]
    [MemberData(nameof(TwoSets_ImprovableData))]
    public void TryImprove_WhenInstanceTwoSets_WithImprovableSolution_ReturnsImprovedSolution(
        int p, int alpha,
        InstanceTwoSets fakeInstance,
        AnpcpSolution mockStartingSolution,
        AnpcpSolution expectedSolution)
    {
        var copiedMockStartingSolution = new AnpcpSolution(mockStartingSolution);
        var stubAfvs = new AlphaFastVertexSubstitution<InstanceTwoSets>(
            fakeInstance,
            p, alpha,
            copiedMockStartingSolution,
            TestSeed);

        var didImprove = stubAfvs.TryImprove();

        var actualSolution = stubAfvs.Solution;

        Assert.True(didImprove);
        Assert.True(
            actualSolution.ObjectiveFunctionValue < mockStartingSolution.ObjectiveFunctionValue);
        Assert.Equal(expectedSolution.CriticalAllocation, actualSolution.CriticalAllocation);
        Assert.Equal(expectedSolution.Centers, actualSolution.Centers);
    }

    public static object[][] TwoSets_LocalOptimumData { get; } = [
        [
            3, 2,
            new InstanceTwoSets(PathHelper.GetAbsolute(@"Data\fake8_4_4.anpcp.tsp")),
            new AnpcpSolution([7], [5, 6, 8], new Allocation(4, 6, 28)),
        ],
        [
            4, 3,
            new InstanceTwoSets(PathHelper.GetAbsolute(@"Data\fake9_4_5.anpcp.tsp")),
            new AnpcpSolution([8], [5, 6, 7, 9], new Allocation(4, 7, 36)),
        ],
    ];

    [Theory]
    [MemberData(nameof(TwoSets_LocalOptimumData))]
    public void TryImprove_WhenInstanceTwoSets_WithLocalOptimum_ReturnsSameSolution(
        int p, int alpha,
        InstanceTwoSets fakeInstance,
        AnpcpSolution mockLocalOptimumSolution)
    {
        var copiedMockStartingSolution = new AnpcpSolution(mockLocalOptimumSolution);
        var stubAfvs = new AlphaFastVertexSubstitution<InstanceTwoSets>(
            fakeInstance,
            p, alpha,
            copiedMockStartingSolution,
            TestSeed);

        var didImprove = stubAfvs.TryImprove();

        var actualSolution = stubAfvs.Solution;

        Assert.False(didImprove);
        Assert.False(
            actualSolution.ObjectiveFunctionValue < mockLocalOptimumSolution.ObjectiveFunctionValue);
        Assert.Equal(mockLocalOptimumSolution.CriticalAllocation, actualSolution.CriticalAllocation);
        Assert.Equal(mockLocalOptimumSolution.Centers, actualSolution.Centers);
    }

    public static object[][] SameSet_ImprovableData { get; } = [
        [
            // p = 3, a = 2
            3, 2,
            new InstanceSameSet(PathHelper.GetAbsolute(@"Data\fake5.tsp")),
            new AnpcpSolution([4, 5], [1, 2, 3], new Allocation(5, 2, 36)),
            new AnpcpSolution([2, 4], [1, 3, 5], new Allocation(4, 3, 22))
        ],
    ];

    [Theory]
    [MemberData(nameof(SameSet_ImprovableData))]
    public void TryImprove_WhenInstanceSameSet_WithImprovableSolution_ReturnsImprovedSolution(
        int p, int alpha,
        InstanceSameSet fakeInstance,
        AnpcpSolution mockStartingSolution,
        AnpcpSolution expectedSolution)
    {
        var copiedMockStartingSolution = new AnpcpSolution(mockStartingSolution);
        var stubAfvs = new AlphaFastVertexSubstitution<InstanceSameSet>(
            fakeInstance,
            p, alpha,
            copiedMockStartingSolution,
            TestSeed);

        var didImprove = stubAfvs.TryImprove();

        var actualSolution = stubAfvs.Solution;

        Assert.True(didImprove);
        Assert.True(
            actualSolution.ObjectiveFunctionValue < mockStartingSolution.ObjectiveFunctionValue);
        Assert.Equal(expectedSolution.CriticalAllocation, actualSolution.CriticalAllocation);
        Assert.Equal(expectedSolution.Centers, actualSolution.Centers);
    }

    public static object[][] SameSet_LocalOptimumData { get; } = [
        [
            3, 2,
            new InstanceSameSet(PathHelper.GetAbsolute(@"Data\fake5.tsp")),
            new AnpcpSolution([2, 4], [1, 3, 5], new Allocation(4, 3, 22)),
        ],
    ];

    [Theory]
    [MemberData(nameof(SameSet_LocalOptimumData))]
    public void TryImprove_WhenInstanceSameSet_WithLocalOptimum_ReturnsSameSolution(
        int p, int alpha,
        InstanceSameSet fakeInstance,
        AnpcpSolution mockLocalOptimumSolution)
    {
        var copiedMockStartingSolution = new AnpcpSolution(mockLocalOptimumSolution);
        var stubAfvs = new AlphaFastVertexSubstitution<InstanceSameSet>(
            fakeInstance,
            p, alpha,
            copiedMockStartingSolution,
            TestSeed);

        var didImprove = stubAfvs.TryImprove();

        var actualSolution = stubAfvs.Solution;

        Assert.False(didImprove);
        Assert.False(
            actualSolution.ObjectiveFunctionValue < mockLocalOptimumSolution.ObjectiveFunctionValue);
        Assert.Equal(mockLocalOptimumSolution.CriticalAllocation, actualSolution.CriticalAllocation);
        Assert.Equal(mockLocalOptimumSolution.Centers, actualSolution.Centers);
    }
}
