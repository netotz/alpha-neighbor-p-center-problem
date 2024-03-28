using Anpcp.Core.Models;

namespace Anpcp.Core.Wrappers;

public class DistancesMatrix
{
    private readonly int[,] _distances;

    public int this[int fromIndex, int toIndex]
        => _distances[fromIndex, toIndex];

    public bool IsInitialized => _distances.Length > 0;

    public DistancesMatrix(Vertex[] vertices1, Vertex[] vertices2)
    {
        _distances = new int[vertices1.Length, vertices2.Length];

        for (var i = 0; i < vertices1.Length; i++)
        {
            for (var j = 0; j < vertices2.Length; j++)
            {
                _distances[i, j] = (int)vertices1[i].DistanceTo(vertices2[j]);
            }
        }
    }
}
