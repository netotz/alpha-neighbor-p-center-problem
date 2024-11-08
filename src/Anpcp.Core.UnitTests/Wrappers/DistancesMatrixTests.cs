using Anpcp.Core.Models;
using Anpcp.Core.Wrappers;

namespace Anpcp.Core.UnitTests.Wrappers;

public class DistancesMatrixTests
{
    public static Vertex[] OneOriginVertices { get; } = [
        new(0, 0, 0)
    ];
    public static Vertex[] TwoVertices1 { get; } = [
        ..OneOriginVertices,
        new(1, 0, 1)
    ];
    public static Vertex[] TwoVertices2 { get; } = [
        new(0, 3, 4),
        new(1, 5, 12)
    ];
    public static Vertex[] ThreeVertices1 { get; } = [
        ..TwoVertices1,
        new(2, 0, 2)
    ];
    public static Vertex[] ThreeVertices2 { get; } = [
        new(0, 8, 15),
        new(1, 5, 12),
        new(2, 7, 24)
    ];

    public static object[][] Data { get; } = [
        // 1 x 1, same set
        [
            OneOriginVertices,
            OneOriginVertices,
            new int[,] { { 0 } },
            (0, 0)
        ],
        // 2 x 2, different sets
        [
            TwoVertices1,
            TwoVertices2,
            new int[,] {
                { 5, 13 },
                { 4, 12 },
            },
            (0, 1)
        ],
        [
            ThreeVertices1,
            ThreeVertices2,
            new int[,] {
                { 17, 13, 25 },
                { 16, 12, 24 },
                { 15, 11, 23 },
            },
            (0, 2)
        ]
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

    public static object[][] SortedData { get; } = [
        [
            new DistancesMatrix(TwoVertices1, TwoVertices2),
            new int[][]
            {
                [0, 1],
                [0, 1],
            }
        ],
        [
            new DistancesMatrix(ThreeVertices1, ThreeVertices2),
            new int[][]
            {
                [1, 0, 2],
                [1, 0, 2],
                [1, 0, 2],
            }
        ]
    ];

    [Theory]
    [MemberData(nameof(SortedData))]
    public void GetNextNearestFacility_ReturnsSortedRow(
        DistancesMatrix distancesMatrix,
        int[][] expectedFacilityIds)
    {
        for (var i = 0; i < expectedFacilityIds.Length; i++)
        {
            var actualFacilityIds = distancesMatrix
                .GetNextNearestFacility(i)
                .ToArray();

            Assert.Equal(expectedFacilityIds[i], actualFacilityIds);
        }
    }
}
