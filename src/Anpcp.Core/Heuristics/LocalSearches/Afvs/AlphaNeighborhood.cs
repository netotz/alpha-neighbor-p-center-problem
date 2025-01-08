using Anpcp.Core.Solutions.Models;
using Anpcp.Core.Wrappers;

namespace Anpcp.Core.Heuristics.LocalSearches.Afvs;

public class AlphaNeighborhood
{
    private readonly Dictionary<int, Allocation> _dictionary;

    /// <summary>
    /// Problem parameter.
    /// </summary>
    public int Alpha { get; }
    public int UserId { get; }
    /// <summary>
    /// Whether or not <see cref="UserId"/> is attracted to a candidate facility to insert.
    /// </summary>
    public bool IsUserAttracted { get; }
    /// <summary>
    /// Distance from <see cref="UserId"/> to its (alpha - 1)th nearest center.
    /// </summary>
    public int AlphaMinusOneDistance => _dictionary[Alpha - 1].Distance;
    /// <summary>
    /// Distance from <see cref="UserId"/> to its alpha-th nearest center.
    /// </summary>
    public int AlphaDistance => _dictionary[Alpha].Distance;
    /// <summary>
    /// Distance from <see cref="UserId"/> to its (alpha + 1)th nearest center.
    /// </summary>
    public int AlphaPlusOneDistance => _dictionary[Alpha + 1].Distance;

    /// <summary>
    /// Creates a wrapper for the alpha-neighbors of <paramref name="userId"/>.
    /// </summary>
    /// <exception cref="KeyNotFoundException"></exception>
    /// <remarks>Time <c>O(p)</c></remarks>
    public AlphaNeighborhood(
        int alpha,
        int userId,
        int fiDistance,
        in HashSet<int> centers,
        in Allocator allocator,
        in DistancesMatrix distancesUF)
    {
        Alpha = alpha;
        UserId = userId;

        _dictionary = new(alpha + 1);

        // O(p)
        foreach (var centerId in centers)
        {
            var proximity = allocator.ById(userId, centerId);

            // ignore empty allocations
            if (proximity == 0)
            {
                continue;
            }

            var distance = distancesUF[userId, centerId];

            _dictionary[proximity] = new Allocation(userId, centerId, distance);

            // when all proximities are found
            if (_dictionary.Count == alpha + 1)
            {
                break;
            }
        }

        if (_dictionary.Count < alpha + 1)
        {
            throw new KeyNotFoundException(
                $"There are missing k-th allocations for user {userId}, " +
                $"found {_dictionary.Keys} but there should be {Enumerable.Range(1, alpha + 1)}. " +
                "Try updating the Allocator before calling this constructor.");
        }

        IsUserAttracted = fiDistance < AlphaDistance;
    }

    /// <summary>
    /// Gets the center IDs that will update the data structures from A-FVS.
    /// See <see cref="AlphaFastVertexSubstitution.GetPotentialSwap(int)"/>.
    /// </summary>
    public IEnumerable<int> GetUpdatingIds()
    {
        return _dictionary
            .Where(p =>
                // always include centers closer than alpha-th
                p.Key < Alpha
                // only ignore alpha-th when user is attracted to fi
                || (!IsUserAttracted || p.Key != Alpha)
                // always ignore a+1
                && p.Key != Alpha + 1)
            .Select(p => p.Value.CenterId);
    }
}
