using Anpcp.Core.Models;

namespace Anpcp.Core.UnitTests.Models;

public class VertexTests
{
    public static object[][] Data { get; } = [
        // same x
        [new Vertex(0, 0, 0), new Vertex(1, 0, 1), 1],
        // same y
        [new Vertex(0, 0, 0), new Vertex(1, 1, 0), 1],
        // diagonals, from https://en.wikipedia.org/wiki/Pythagorean_triple#Examples
        [new Vertex(0, 0, 0), new Vertex(1, 3, 4), 5],
        [new Vertex(0, 0, 0), new Vertex(1, 5, 12), 13],
        [new Vertex(0, 0, 0), new Vertex(1, 65, 72), 97],
    ];

    [Theory]
    [MemberData(nameof(Data))]
    public void DistanceTo_ReturnsEuclideanDistance(Vertex v1, Vertex v2, double expectedDistance)
    {
        var actual = v1.DistanceTo(v2);

        Assert.Equal(expectedDistance, actual);
    }
}
