using Anpcp.Core.Heuristics.LocalSearches.Afvs.Models;
using Anpcp.Core.Heuristics.LocalSearches.Afvs.Wrappers;

namespace Anpcp.Core.UnitTests.Heuristics.LocalSearches.Afvs;

public class LargestTwoGainsTests
{
    public static object[][] Data { get; } = [
        [
            new Dictionary<int, int>
            {
                { 0, 1 },
                { 1, 0 },
            },
            new GainsFacility(0, 1),
            new GainsFacility(1, 0)
        ],
        [
            new Dictionary<int, int>
            {
                { 0, 0 },
                { 1, 9 },
                { 2, 2 },
                { 3, 5 },
            },
            new GainsFacility(1, 9),
            new GainsFacility(3, 5)
        ]
    ];

    [Theory]
    [MemberData(nameof(Data))]
    public void Constructor_SetsFirstAndSecond(
        Dictionary<int, int> stubGainsNeighbors,
        GainsFacility expectedFirst,
        GainsFacility expectedSecond)
    {
        var stubLargestTwoGains = new LargestTwoGains(stubGainsNeighbors);

        var actualFirst = stubLargestTwoGains.First;
        var actualSecond = stubLargestTwoGains.Second;

        Assert.Equal(expectedFirst, actualFirst);
        Assert.Equal(expectedSecond, actualSecond);
    }
}
