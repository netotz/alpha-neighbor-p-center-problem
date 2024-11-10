using Anpcp.Core.Models;

namespace Anpcp.Core.Wrappers;

public class DistancesMatrix
{
    private readonly int[,] _distances;
    /// <summary>
    /// Sorted distances where each cell is a tuple <c>(distance, facilityId)</c>.
    /// </summary>
    private readonly (int, int)[][] _sortedDistances;

    public int this[int fromIndex, int toIndex]
        => _distances[fromIndex, toIndex];

    public bool IsInitialized => _distances?.Length > 0;
    public (int, int) Dimensions => (_distances.GetLength(0), _distances.GetLength(1));

    /// <summary>
    /// Indices pair of vertices whose distance is the maximum in the matrix.
    /// </summary>
    public (int, int) MaxPair { get; private set; }

    public DistancesMatrix()
    {
        _distances = new int[0, 0];
        _sortedDistances = [];
        MaxPair = (-1, -1);
    }

    public DistancesMatrix(Vertex[] vertices1, Vertex[] vertices2)
    {
        var n = vertices1.Length;
        var m = vertices2.Length;

        _distances = new int[n, m];
        _sortedDistances = new (int, int)[n][];

        // current maximum distance in the matrix
        var currentMax = int.MinValue;

        //// O(nm log m)
        // O(n)
        for (var i = 0; i < n; i++)
        {
            var unsortedRow = new List<int>(m);

            // O(m)
            for (var j = 0; j < m; j++)
            {
                var distance = (int)vertices1[i].DistanceTo(vertices2[j]);
                _distances[i, j] = distance;

                if (distance > currentMax)
                {
                    currentMax = distance;
                    MaxPair = (i, j);
                }

                unsortedRow.Add(distance);
            }

            // O(m log m)
            var sortedRow = unsortedRow
                .Select((distance, index) => (distance, index))
                .OrderBy(s => s.distance)
                .ToArray();

            _sortedDistances[i] = sortedRow;
        }
    }

    /// <remarks>Time O(m)</remarks>
    public IEnumerable<int> GetNextNearestFacility(int fromUser)
    {
        // O(m)
        foreach (var (_, facilityId) in _sortedDistances[fromUser])
        {
            yield return facilityId;
        }
    }
}
