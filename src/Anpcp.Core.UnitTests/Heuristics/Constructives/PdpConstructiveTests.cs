using Anpcp.Core.Heuristics.Constructives;

namespace Anpcp.Core.UnitTests.Heuristics.Constructives;

/// <summary>
/// Tests of constructive heuristics that solve the PDP:
/// <see cref="FgdConstructive"/> and <see cref="OgdConstructive"/>.
/// </summary>
public class PdpConstructiveTests
{
    public static int? TestSeed { get; } = 20240402;
    public static InstanceSameSet RandomInstance_m5 { get; } = new(5, 100, 100, TestSeed);

    public static object[][] Data { get; } = [
        [RandomInstance_m5, 2, 2, 3],
        [RandomInstance_m5, 4, 4, 1],
    ];

    [Theory]
    [MemberData(nameof(Data))]
    public void Fgd_Construct_ReturnsSolutionWithPFacilities(
        InstanceSameSet instance,
        int p,
        int expectedP,
        int expectedCloseds)
    {
        var stubConstructive = new FgdConstructive(instance, p, TestSeed);

        var mockSolution = stubConstructive.Construct();

        Assert.Equal(mockSolution.OpenFacilities.Count, expectedP);
        Assert.Equal(mockSolution.ClosedFacilities.Count, expectedCloseds);
    }

    [Theory]
    [MemberData(nameof(Data))]
    public void Ogd_Construct_ReturnsSolutionWithPFacilities(
    InstanceSameSet instance,
    int p,
    int expectedP,
    int expectedCloseds)
    {
        var stubConstructive = new OgdConstructive(instance, p, TestSeed);

        var mockSolution = stubConstructive.Construct();

        Assert.Equal(mockSolution.OpenFacilities.Count, expectedP);
        Assert.Equal(mockSolution.ClosedFacilities.Count, expectedCloseds);
    }
}
