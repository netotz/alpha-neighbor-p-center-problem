namespace Anpcp.Core.UnitTests;

public class InstanceTests
{
    public static object[][] Data { get; } = [
        [1, 1, 0, 1, 1],
        [100, 100, 0, 100, 100],
    ];

    [Theory]
    [MemberData(nameof(Data))]
    public void Constructor_CreatesInstance(
        int n, int m, int? seed, int expectedN, int expectedM)
    {
        var actual = new Instance(n, m, seed: seed);

        Assert.Equal(actual.Users.Length, expectedN);
        Assert.Equal(actual.Facilities.Length, expectedM);
    }
}
