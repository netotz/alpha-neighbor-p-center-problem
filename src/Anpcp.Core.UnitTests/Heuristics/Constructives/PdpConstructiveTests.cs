using Anpcp.Core.Heuristics.Constructives;

namespace Anpcp.Core.UnitTests.Heuristics.Constructives;

/// <summary>
/// Tests of constructive heuristics that solve the PDP:
/// <see cref="FgdConstructive"/> and <see cref="OgdConstructive"/>.
/// </summary>
public class PdpConstructiveTests
{
    public static int? TestSeed { get; } = 20240402;
    public static InstanceSameSet SeededInstance_m5 { get; } = new(5, 100, 100, TestSeed);
    public static InstanceSameSet SeededInstance_m10 { get; } = new(10, 100, 100, TestSeed);

    public static object[][] Data { get; } = [
        [SeededInstance_m5, 2, 3],
        [SeededInstance_m5, 4, 1],
        [SeededInstance_m10, 5, 5],
        [SeededInstance_m10, 9, 1],
    ];

    /// <summary>
    /// Both heuristics should return the same solution:
    /// same set of open facilities and same objective function value.
    /// </summary>
    [Theory]
    [MemberData(nameof(Data))]
    public void OgdAndFgd_Construct_ReturnSameSolution(
        InstanceSameSet instance,
        int p,
        int expectedCloseds)
    {
        var stubOgd = new OgdConstructive(instance, p, TestSeed);
        var stubFgd = new FgdConstructive(instance, p, TestSeed);

        var mockOgdSolution = stubOgd.Construct();
        mockOgdSolution.UpdateObjectiveFunctionValue(instance);

        var mockFgdSolution = stubFgd.Construct();

        Assert.Equal(mockOgdSolution.OpenFacilities, mockFgdSolution.OpenFacilities);

        Assert.Equal(mockOgdSolution.ObjectiveFunctionValue, mockFgdSolution.ObjectiveFunctionValue);

        Assert.Equal(expectedCloseds, mockOgdSolution.ClosedFacilities.Count);
        Assert.Equal(expectedCloseds, mockFgdSolution.ClosedFacilities.Count);
    }
}
