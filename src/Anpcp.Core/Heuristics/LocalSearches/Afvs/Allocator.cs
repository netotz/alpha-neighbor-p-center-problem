using System.Collections.Immutable;

using Anpcp.Core.Wrappers;

namespace Anpcp.Core.Heuristics.LocalSearches.Afvs;

public class Allocator(int alpha, int n, int m, in IdIndexMap idIndexMap)
{
    private readonly int[,] _allocations = new int[n, m];
    private readonly IdIndexMap _idIndexMap = idIndexMap;

    /// <summary>
    /// Gets the allocation by IDs, mapping them to indices of the matrix.
    /// </summary>
    /// <param name="userId"></param>
    /// <param name="facilityId"></param>
    /// <returns></returns>
    public int ById(int userId, int facilityId)
    {
        var userIndex = _idIndexMap.Users[userId];
        var facilityIndex = _idIndexMap.Facilities[facilityId];

        return _allocations[userIndex, facilityIndex];
    }

    public int ByIndex(int userIndex, int facilityIndex)
    {
        return _allocations[userIndex, facilityIndex];
    }

    private void SetById(int userId, int facilityId, int value)
    {
        var userIndex = _idIndexMap.Users[userId];
        var facilityIndex = _idIndexMap.Facilities[facilityId];

        _allocations[userIndex, facilityIndex] = value;
    }

    private void SetByIndex(int userIndex, int facilityIndex, int value)
    {
        _allocations[userIndex, facilityIndex] = value;
    }

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
            // ignore facilities outside solution
            if (!centers.Contains(facilityId))
            {
                continue;
            }

            proximity++;
            // no need to allocate facilities farther than (alpha+1)-th
            if (proximity > alpha + 1)
            {
                break;
            }

            SetById(userId, facilityId, proximity);
        }
    }

    /// <summary>
    /// Deallocates a user from all facilities.
    /// </summary>
    /// <remarks>Time O(m)</remarks>
    private void DeallocateUser(int userId)
    {
        var userIndex = _idIndexMap.Users[userId];

        // O(m)
        for (var j = 0; j < m; j++)
        {
            SetByIndex(userIndex, j, 0);
        }
    }
}
