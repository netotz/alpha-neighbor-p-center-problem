using System.Runtime.CompilerServices;

using Anpcp.Core.IO;
using Anpcp.Core.Models;
using Anpcp.Core.Models.Enums;

namespace Anpcp.Core.UnitTests.IO;

public class TspFileIOTests
{
    public static object[][] Data { get; } = [
        [
            GetAbsolutePath(@"Data\test1.anpcp.tsp"),
            new List<Vertex> { new(1, 0, 0, VertexType.User) }
        ],
        [
            GetAbsolutePath(@"Data\test2.anpcp.tsp"),
            new List<Vertex> {
                new(1, 1, 1, VertexType.User),
                new(2, 2, 2, VertexType.User),
                new(3, 3, 3, VertexType.Facility),
                new(4, 4, 4, VertexType.Facility),
            }
        ],
        [
            GetAbsolutePath(@"Data\test3.tsp"),
            new List<Vertex> {
                new(1, 1, 1),
                new(2, 2, 2),
            }
        ],
    ];

    [Theory]
    [MemberData(nameof(Data))]
    public void ReadNodes_ReturnsListOfVertex(string filePath, List<Vertex> expectedVertices)
    {
        var actualVertices = TspFileIO.ReadNodes(filePath);

        Assert.Equal(actualVertices, expectedVertices);
    }

    private static string GetAbsolutePath(string filePath, [CallerFilePath] string currentPath = "")
    {
        var currentDirectory = Path.GetDirectoryName(currentPath) ?? "";

        return Path.Combine(currentDirectory, filePath);
    }
}
