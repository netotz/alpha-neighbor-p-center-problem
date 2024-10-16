using Anpcp.Core.Models;

namespace Anpcp.Core.Wrappers;

public class DistancesMatrix
{
    private readonly int[,] _distances;

    public int this[int fromIndex, int toIndex]
        => _distances[fromIndex, toIndex];

    public bool IsInitialized => _distances?.Length > 0;

    /// <summary>
    /// Indices pair of vertices whose distance is the maximum in the matrix.
    /// </summary>
    public (int, int) MaxPair { get; private set; }

    public DistancesMatrix()
    {
        _distances = new int[0, 0];
        MaxPair = (-1, -1);
    }

    public DistancesMatrix(Vertex[] vertices1, Vertex[] vertices2)
    {
        _distances = new int[vertices1.Length, vertices2.Length];

        // current maximum distance in the matrix
        var currentMax = int.MinValue;

        for (var i = 0; i < vertices1.Length; i++)
        {
            for (var j = 0; j < vertices2.Length; j++)
            {
                var distance = (int)vertices1[i].DistanceTo(vertices2[j]);
                _distances[i, j] = distance;

                if (distance > currentMax)
                {
                    currentMax = distance;
                    MaxPair = (i, j);
                }
            }
        }
    }
}
