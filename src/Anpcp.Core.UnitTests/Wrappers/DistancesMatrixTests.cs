using Anpcp.Core.Models;
using Anpcp.Core.Wrappers;

namespace Anpcp.Core.UnitTests.Wrappers;

public class DistancesMatrixTests
{
    public static object[][] Data { get; } = [
        // 1 x 1, same set
        [
            new Vertex[] { new(0, 0, 0) },
            new Vertex[] { new(0, 0, 0) },
            new int[,] { { 0 } },
            (0, 0)
        ],
        // 2 x 2, different sets
        [
            new Vertex[] { new(0, 0, 0), new(1, 0, 1) },
            new Vertex[] { new(0, 3, 4), new(1, 5, 12) },
            new int[,] {
                { 5, 13 },
                { 4, 12 },
            },
            (0, 1)
        ],
    ];

    [Theory]
    [MemberData(nameof(Data))]
    public void Constructor_InstantiatesDistancesMatrixCorrectly(
        Vertex[] v1,
        Vertex[] v2,
        int[,] expectedDistances,
        (int, int) expectedMaxPair)
    {
        var mockMatrix = new DistancesMatrix(v1, v2);

        Assert.True(mockMatrix.IsInitialized);
        Assert.Equal(mockMatrix.MaxPair, expectedMaxPair);

        var areEquals = new List<bool>();
        for (var i = 0; i < v1.Length; i++)
        {
            for (var j = 0; j < v2.Length; j++)
            {
                areEquals.Add(mockMatrix[i, j] == expectedDistances[i, j]);
            }
        }

        Assert.True(areEquals.All(a => a));
    }
}
