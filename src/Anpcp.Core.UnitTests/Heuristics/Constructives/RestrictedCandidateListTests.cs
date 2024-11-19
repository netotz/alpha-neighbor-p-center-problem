using Anpcp.Core.Heuristics.Constructives.Rgd;

namespace Anpcp.Core.UnitTests.Heuristics.Constructives;

public class RestrictedCandidateListTests
{
    public const int BETA_0 = 0;
    public static int TestSeed => 0;

    public static object[][] Data { get; } = [
        [
            new [] {
                (0, 20),
                (1, 10),
                (2, 30),
            },
            2
        ]
    ];

    [Theory]
    [MemberData(nameof(Data))]
    public void GetFacilityToInsert_WhenBetaIs0_ReturnsFacilityWithMaxDistance(
        (int, int)[] candidates,
        int expectedFacilityToInsert)
    {
        var stubRestrictedCandidateList = new RestrictedCandidateList(BETA_0, TestSeed);

        foreach (var (facilityId, distance) in candidates)
        {
            stubRestrictedCandidateList.Add(facilityId, distance);
        }

        var actualFacilityToInsert = stubRestrictedCandidateList.GetFacilityToInsert();

        Assert.Equal(expectedFacilityToInsert, actualFacilityToInsert);
    }
}
