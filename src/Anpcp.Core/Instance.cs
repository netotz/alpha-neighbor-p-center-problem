using Anpcp.Core.Enums;
using Anpcp.Core.IO;
using Anpcp.Core.Models;
using Anpcp.Core.Wrappers;

namespace Anpcp.Core;

/// <summary>
/// An instance of the ANPCP with two sets of nodes for users and facilities.
/// </summary>
public class Instance
{
    public Vertex[] Facilities { get; protected set; }
    public IEnumerable<int> FacilitiesIndices => Facilities.Select(f => f.Index);
    public Vertex[] Users { get; protected set; }
    public IEnumerable<int> UsersIndices => Users.Select(u => u.Index);
    /// <summary>
    /// Matrix of distances between users and facilities.
    /// </summary>
    public DistancesMatrix DistancesUF { get; private set; }
    /// <summary>
    /// Matrix of distances between facilities.
    /// </summary>
    public DistancesMatrix DistancesFF { get; private set; }

    /// <summary>
    /// Dummy constructor for child class <see cref="InstanceSameSet"/>.
    /// </summary>
    protected Instance() { }

    /// <summary>
    /// Creates an instance from a ANPCP TSPLIB file, our custom variation.
    /// </summary>
    /// <remarks>
    /// The extension must be <c>*.anpcp.tsp</c>
    /// </remarks>
    public Instance(string tspFilePath)
    {
        var vertices = TspFileIO.ReadNodes(tspFilePath);

        Facilities = vertices
            .Where(v => v.Type is VertexType.Facility)
            .ToArray();
        Users = vertices
            .Where(v => v.Type is VertexType.User)
            .ToArray();

        InitDistancesMatrices();
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
        // O(n + m)
        Users = distinctCoords
            .Skip(m)
            .Take(n)
            .Select((c, i) => new Vertex(i, c.x, c.y))
            .ToArray();

        InitDistancesMatrices();
    }

    protected void InitDistancesMatrices()
    {
        DistancesFF = new(Facilities, Facilities);
        DistancesUF = new(Users, Facilities);
    }
}
