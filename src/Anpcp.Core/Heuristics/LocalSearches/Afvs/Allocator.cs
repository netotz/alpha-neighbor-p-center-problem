using System.Collections.Immutable;

namespace Anpcp.Core.Heuristics.LocalSearches.Afvs;

public class Allocator(int alpha, int n, int m)
{
    private readonly int[,] _allocations = new int[n, m];

    /// <summary>
    /// Gets a value in the allocations matrix.
    /// </summary>
    public int this[int userId, int facilityId] => _allocations[userId, facilityId];

    /// <summary>
    /// Allocates all users to their alpha-neighbors.
    /// </summary>
    /// <param name="nearestFacilitiesGetter">
    /// A delegate that enumerates in order the nearest facilities of a user.
    /// </param>
    /// <remarks>Time O(nm)</remarks>
    public void AllocateAll(
        ImmutableHashSet<int> userIds,
        Func<int, IEnumerable<int>> nearestFacilitiesGetter,
        HashSet<int> centers)
    {
        //// O(nm)
        // O(n)
        foreach (var userId in userIds)
        {
            var nearestFacilities = nearestFacilitiesGetter(userId);
            // O(m)
            ReallocateUser(userId, nearestFacilities, centers);
        }
    }

    /// <remarks>Time O(m)</remarks>
    private void ReallocateUser(
        int userId,
        IEnumerable<int> nearestFacilities,
        HashSet<int> centers)
    {
        // O(m)
        DeallocateUser(userId);

        var proximity = 0;
        // O(m)
        foreach (var facilityId in nearestFacilities)
        {
            // no need to allocate facilities farther than (alpha+1)-th
            if (proximity > alpha + 1)
            {
                break;
            }

            // ignore facilities outside solution
            if (!centers.Contains(facilityId))
            {
                continue;
            }

            proximity++;
            _allocations[userId, facilityId] = proximity;
        }
    }

    /// <summary>
    /// Deallocates a user from all facilities.
    /// </summary>
    /// <remarks>Time O(m)</remarks>
    private void DeallocateUser(int userId)
    {
        // O(m)
        for (var j = 0; j < m; j++)
        {
            _allocations[userId, j] = 0;
        }
    }
}
