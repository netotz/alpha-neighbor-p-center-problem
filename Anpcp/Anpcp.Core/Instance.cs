using Anpcp.Core.Models;
using Anpcp.Core.Wrappers;

namespace Anpcp.Core;

/// <summary>
/// An instance of the ANPCP.
/// </summary>
public class Instance
{
    public Vertex[] Facilities { get; }
    public Vertex[] Users { get; }
    /// <summary>
    /// Matrix of distances between users and facilities.
    /// </summary>
    public DistancesMatrix DistancesUF { get; }
    /// <summary>
    /// Matrix of distances between facilities.
    /// </summary>
    public DistancesMatrix DistancesFF { get; }

    public Instance(string tspFilePath)
    {
        throw new NotImplementedException();
    }

    /// <summary>
    /// Randomly constructs an instance of <c>n</c> users and <c>m facilities</c> on a 2D plane
    /// with coordinates [0, <c>xAxisMax</c>], [0, <c>yAxisMax</c>].
    /// </summary>
    /// <param name="n">Amount of users.</param>
    /// <param name="m">Amount of facilities.</param>
    /// <param name="xAxisMax">Maximum coordinate for x-axis. Default is 1000.</param>
    /// <param name="yAxisMax">Maximum coordinate for y-axis. Default is 1000.</param>
    /// <param name="seed">Seed for random generator. Default is null, which uses a random seed.</param>
    public Instance(int n, int m, int xAxisMax = 1000, int yAxisMax = 1000, int? seed = null)
    {
        var random = seed is null ? new Random() : new Random((int)seed);

        var distinctCoords = new HashSet<(int x, int y)>();

        // O(n + m)
        while (distinctCoords.Count < n + m)
        {
            var randomCoord = (random.Next(xAxisMax), random.Next(yAxisMax));
            distinctCoords.Add(randomCoord);
        }

        // O(m)
        Facilities = distinctCoords
            .Take(m)
            .Select((c, i) => new Vertex(i, c.x, c.y))
            .ToArray();

        DistancesFF = new(Facilities, Facilities);

        // O(n + m)
        Users = distinctCoords
            .Skip(m)
            .Take(n)
            .Select((c, i) => new Vertex(i, c.x, c.y))
            .ToArray();

        DistancesUF = new(Users, Facilities);
    }
}
