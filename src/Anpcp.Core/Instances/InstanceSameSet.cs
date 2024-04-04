using Anpcp.Core.IO;
using Anpcp.Core.Models;

namespace Anpcp.Core.Instances;

/// <summary>
/// An instance of the ANPCP with one set of nodes for both users and facilities.
/// </summary>
public class InstanceSameSet : BaseInstance
{
    /// <summary>
    /// Creates an instance from a TSPLIB file.
    /// </summary>
    /// <remarks>
    /// The extension must be <c>*.tsp</c>
    /// </remarks>
    public InstanceSameSet(string tspFilePath)
    {
        Name = Path.GetFileNameWithoutExtension(tspFilePath);

        var vertices = TspFileIO.ReadNodes(tspFilePath).ToArray();

        Facilities = vertices;

        DistancesFF = new(Facilities, Facilities);

        Users = vertices;

        DistancesUF = new(Users, Facilities);
    }

    /// <summary>
    /// Randomly constructs an instance of <c>n</c> vertices on a 2D plane
    /// with coordinates [0, <c>xAxisMax</c>], [0, <c>yAxisMax</c>].
    /// </summary>
    /// <param name="n">Amount of vertices.</param>
    /// <param name="xAxisMax">Maximum coordinate for x-axis. Default is 1000.</param>
    /// <param name="yAxisMax">Maximum coordinate for y-axis. Default is 1000.</param>
    /// <param name="seed">Seed for random generator. Default is null, which uses a random seed.</param>
    public InstanceSameSet(int n, int xAxisMax = 1000, int yAxisMax = 1000, int? seed = null)
    {
        var random = seed is null ? new Random() : new Random(seed.Value);

        var distinctCoords = new HashSet<(int x, int y)>();

        // O(n)
        while (distinctCoords.Count < n)
        {
            var randomCoord = (random.Next(xAxisMax), random.Next(yAxisMax));
            distinctCoords.Add(randomCoord);
        }

        // O(n)
        Facilities = distinctCoords
            .Take(n)
            .Select((c, i) => new Vertex(i, c.x, c.y))
            .ToArray();

        DistancesFF = new(Facilities, Facilities);

        Users = Facilities;

        DistancesUF = new(Users, Facilities);
    }
}
