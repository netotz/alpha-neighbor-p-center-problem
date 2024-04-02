using Anpcp.Core.Heuristics.Constructives;

namespace Anpcp.Core.UnitTests.Heuristics.Constructives;

public class PdpConstructiveTests
{
    public static int? TestSeed { get; } = 20240402;
    public static Instance RandomInstance_m5 { get; } = new(0, 5, 100, 100, TestSeed);

    public static object[][] Data { get; } = [
        [RandomInstance_m5, 2, 2, 3],
        [RandomInstance_m5, 4, 4, 1],
    ];

    [Theory]
    [MemberData(nameof(Data))]
    public void Construct_ReturnsSolutionWithPFacilities(
        Instance instance,
        int p,
        int expectedP,
        int expectedCloseds)
    {
        var stubConstructive = new PdpConstructive(instance, p, TestSeed);

        var mockSolution = stubConstructive.Construct();

        Assert.Equal(mockSolution.OpenFacilities.Count, expectedP);
        Assert.Equal(mockSolution.ClosedFacilities.Count, expectedCloseds);
    }
}
