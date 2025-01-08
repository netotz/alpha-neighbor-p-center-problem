using Anpcp.Core.Instances;
using Anpcp.Core.Solutions;
using Anpcp.Core.Solutions.Models;

namespace Anpcp.Core.UnitTests.Solutions;

public class PdpSolutionTests
{
    public static int? TestSeed => 20240402;
    /// <summary>
    /// Distances matrix (seed = 20240402):
    ///  0  1  2  3  4
    /// [0 66 12 50 63] 0
    /// [66 0 64 18 45] 1
    /// [12 64 0 51 69] 2
    /// [50 18 51 0 32] 3
    /// [63 45 69 32 0] 4
    /// </summary>
    public static InstanceSameSet SeededInstance_m5 { get; } = new(5, 100, 100, TestSeed);

    public static object[][] Data { get; } = [
        [
            SeededInstance_m5,
            CreateSolution_WithOpenFacilities(5, [0, 1]),
            new Allocation(0, 1, 66)
        ],
        [
            SeededInstance_m5,
            CreateSolution_WithOpenFacilities(5, [0, 1, 2]),
            new Allocation(0, 2, 12)
        ],
        [
            SeededInstance_m5,
            CreateSolution_WithOpenFacilities(5, [0, 1, 2, 3]),
            new Allocation(0, 2, 12)
        ],
        [
            SeededInstance_m5,
            CreateSolution_WithOpenFacilities(5, [2, 3, 4]),
            new Allocation(3, 4, 32)
        ],
    ];

    [Theory]
    [MemberData(nameof(Data))]
    public void UpdateObjectiveFunctionValue_ReturnsMinimumDistance(
        InstanceSameSet instance,
        PdpSolution solution,
        Allocation expectedCriticalAllocation)
    {
        var actual = solution.UpdateCriticalAllocation(instance.DistancesFF);

        Assert.Equal(expectedCriticalAllocation, solution.CriticalAllocation);
    }

    private static PdpSolution CreateSolution_WithOpenFacilities(
        int totalFacilitiesAmount,
        IEnumerable<int> openFacilities)
    {
        var closedFacilities = Enumerable
            .Range(0, totalFacilitiesAmount)
            .ToHashSet();

        var solution = new PdpSolution(closedFacilities);

        foreach (var fi in openFacilities)
            solution.Insert(fi);

        return solution;
    }
}
