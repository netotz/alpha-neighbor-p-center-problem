using Anpcp.Core.IO;
using Anpcp.Core.Models;
using Anpcp.Core.Models.Enums;

namespace Anpcp.Core.UnitTests.IO;

public class TspFileIOTests
{
    public static object[][] Data { get; } = [
        [
            PathHelper.GetAbsolute(@"Data\test1.anpcp.tsp"),
            new List<Vertex> { new(0, 0, 0, VertexType.User) }
        ],
        [
            PathHelper.GetAbsolute(@"Data\test2.anpcp.tsp"),
            new List<Vertex> {
                new(0, 1, 1, VertexType.User),
                new(1, 2, 2, VertexType.User),
                new(2, 3, 3, VertexType.Facility),
                new(3, 4, 4, VertexType.Facility),
            }
        ],
        [
            PathHelper.GetAbsolute(@"Data\test3.tsp"),
            new List<Vertex> {
                new(0, 1, 1),
                new(1, 2, 2),
            }
        ]
    ];

    [Theory]
    [MemberData(nameof(Data))]
    public void ReadNodes_ReturnsListOfVertex(string filePath, List<Vertex> expectedVertices)
    {
        var actualVertices = TspFileIO.ReadNodes(filePath);

        Assert.Equal(expectedVertices, actualVertices);
    }

    public static object[][] RepeatedData { get; } = [
        [
            PathHelper.GetAbsolute(@"Data\test4.anpcp.tsp"),
            new List<Vertex> { new(0, 0, 0, VertexType.User) }
        ]
    ];

    [Theory]
    [MemberData(nameof(RepeatedData))]
    public void ReadNodes_WhenRepeatedCoordinates_ReturnsUniqueListOfVertex(string filePath, List<Vertex> expectedVertices)
    {
        var actualVertices = TspFileIO.ReadNodes(filePath);

        Assert.Equal(expectedVertices, actualVertices);
    }
}
