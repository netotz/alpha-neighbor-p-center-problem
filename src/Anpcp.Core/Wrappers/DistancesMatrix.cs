using Anpcp.Core.Models;

namespace Anpcp.Core.Wrappers;

public class DistancesMatrix
{
    private readonly int[,] _distances;
    /// <summary>
    /// Sorted distances where each cell is a tuple <c>(distance, facilityId)</c>.
    /// </summary>
    private readonly (int Distance, int FacilityId)[][] _sortedDistances;

    public IdIndexMap IdIndexMap { get; }
    public int this[int fromId, int toId]
    {
        get
        {
            var fromIndex = IdIndexMap.Users[fromId];
            var toIndex = IdIndexMap.Facilities[toId];

            return _distances[fromIndex, toIndex];
        }
    }

    public bool IsInitialized => _distances?.Length > 0;
    public (int, int) Dimensions => (_distances.GetLength(0), _distances.GetLength(1));

    /// <summary>
    /// Indices pair of vertices whose distance is the maximum in the matrix.
    /// </summary>
    public (int, int) MaxPair { get; private set; }

    public DistancesMatrix()
    {
        IdIndexMap = new IdIndexMap([], []);

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

        var rowIdIndexDictionary = new Dictionary<int, int>();
        var columnIdIndexDictionary = new Dictionary<int, int>();

        //// O(nm log m)
        // O(n)
        for (var i = 0; i < n; i++)
        {
            var unsortedRow = new List<(int Distance, int FacilityId)>(m);

            var vertex1 = vertices1[i];
            rowIdIndexDictionary[vertex1.Id] = i;

            // O(m)
            for (var j = 0; j < m; j++)
            {
                var vertex2 = vertices2[j];
                columnIdIndexDictionary[vertex2.Id] = j;

                var distance = (int)vertex1.DistanceTo(vertex2);
                _distances[i, j] = distance;

                if (distance > currentMax)
                {
                    currentMax = distance;
                    MaxPair = (i, j);
                }

                unsortedRow.Add((distance, vertex2.Id));
            }

            // O(m log m)
            var sortedRow = unsortedRow
                .OrderBy(t => t.Distance)
                .ToArray();

            _sortedDistances[i] = sortedRow;
        }

        // O(n + m)
        IdIndexMap = new IdIndexMap(rowIdIndexDictionary, columnIdIndexDictionary);
    }

    /// <remarks>Time O(m)</remarks>
    public IEnumerable<int> GetNextNearestFacility(int fromUserId)
    {
        var userIndex = IdIndexMap.Users[fromUserId];

        // O(m)
        foreach (var (_, facilityId) in _sortedDistances[userIndex])
        {
            yield return facilityId;
        }
    }
}
