using Anpcp.Core.Heuristics.LocalSearches.Afvs;
using Anpcp.Core.Instances;
using Anpcp.Core.Solutions;
using Anpcp.Core.Solutions.Models;

namespace Anpcp.Core.UnitTests.Heuristics.LocalSearches.Afvs;

public class AlphaFastVertexSubstitutionTests
{
    public static InstanceTwoSets DummyInstance { get; } = new(1, 1, seed: 0);
    public static AnpcpSolution EmptySolution { get; } = new([]);
    public static object[][] ExceptionData { get; } = [
        // a == p
        [2, 2, DummyInstance, EmptySolution],
        // |S| < p
        [3, 2, DummyInstance, EmptySolution],
    ];

    [Theory]
    [MemberData(nameof(ExceptionData))]
    public void Constructor_ThrowsArgumentException(
        int p, int alpha,
        InstanceTwoSets dummyInstance,
        AnpcpSolution emptySolution)
    {
        Assert.Throws<ArgumentException>(()
            => new AlphaFastVertexSubstitution(p, alpha, dummyInstance, emptySolution));
    }

    public static object[][] ImprovedData { get; } = [
        [
            // p = 3, a = 2
            3, 2,
            new InstanceTwoSets(PathHelper.GetAbsolute(@"Data\fake8_4_4.anpcp.tsp")),
            new AnpcpSolution([0], [1, 2, 3], new Allocation(3, 2, 36)),
            new AnpcpSolution([2], [0, 1, 3], new Allocation(3, 1, 28))
        ],
        [
            3, 2,
            new InstanceTwoSets(PathHelper.GetAbsolute(@"Data\fake9_4_5.anpcp.tsp")),
            new AnpcpSolution([0, 1], [2, 3, 4], new Allocation(3, 3, 53)),
            new AnpcpSolution([2, 3], [0, 1, 4], new Allocation(3, 1, 28))
        ],
        [
            4, 3,
            new InstanceTwoSets(PathHelper.GetAbsolute(@"Data\fake9_4_5.anpcp.tsp")),
            new AnpcpSolution([0], [1, 2, 3, 4], new Allocation(3, 3, 53)),
            new AnpcpSolution([3], [0, 1, 2, 4], new Allocation(3, 2, 36))
        ],
    ];

    [Theory]
    [MemberData(nameof(ImprovedData))]
    public void Improve_WithImprovableSolution_ReturnsImprovedSolution(
        int p, int alpha,
        InstanceTwoSets fakeInstance,
        AnpcpSolution mockStartingSolution,
        AnpcpSolution expectedSolution)
    {
        var copiedMockStartingSolution = new AnpcpSolution(mockStartingSolution);
        var stubAfvs = new AlphaFastVertexSubstitution(
            p, alpha,
            fakeInstance,
            copiedMockStartingSolution);

        var didImprove = stubAfvs.TryImprove();
        var actualSolution = stubAfvs.Solution;

        Assert.True(didImprove);
        Assert.True(
            actualSolution.ObjectiveFunctionValue < mockStartingSolution.ObjectiveFunctionValue);
        Assert.Equal(expectedSolution.CriticalAllocation, actualSolution.CriticalAllocation);
        Assert.Equal(expectedSolution.Centers, actualSolution.Centers);
    }

    public static object[][] LocalOptimumData { get; } = [
        [
            3, 2,
            new InstanceTwoSets(PathHelper.GetAbsolute(@"Data\fake8_4_4.anpcp.tsp")),
            new AnpcpSolution([2], [0, 1, 3], new Allocation(3, 1, 28)),
        ],
        [
            4, 3,
            new InstanceTwoSets(PathHelper.GetAbsolute(@"Data\fake9_4_5.anpcp.tsp")),
            new AnpcpSolution([3], [0, 1, 2, 4], new Allocation(3, 2, 36)),
        ],
    ];

    [Theory]
    [MemberData(nameof(LocalOptimumData))]
    public void Improve_WithLocalOptimum_ReturnsSameSolution(
        int p, int alpha,
        InstanceTwoSets fakeInstance,
        AnpcpSolution mockLocalOptimumSolution)
    {
        var copiedMockStartingSolution = new AnpcpSolution(mockLocalOptimumSolution);
        var stubAfvs = new AlphaFastVertexSubstitution(
            p, alpha,
            fakeInstance,
            copiedMockStartingSolution);

        var didImprove = stubAfvs.TryImprove();
        var actualSolution = stubAfvs.Solution;

        Assert.False(didImprove);
        Assert.False(
            actualSolution.ObjectiveFunctionValue < mockLocalOptimumSolution.ObjectiveFunctionValue);
        Assert.Equal(mockLocalOptimumSolution.CriticalAllocation, actualSolution.CriticalAllocation);
        Assert.Equal(mockLocalOptimumSolution.Centers, actualSolution.Centers);
    }
}
