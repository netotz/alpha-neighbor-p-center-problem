using Anpcp.Core.Instances;

namespace Anpcp.Core.Heuristics.Constructives.Rgd;

/// <summary>
/// Randomized Greedy Dispersion (RGD) constructive heuristic to use within GRASP.
/// Solves the p-dispersion problem (PDP).
/// </summary>
/// <remarks>Inherits from <see cref="FastGreedyDispersion{TInstance}"/>.</remarks>
public class RandomizedGreedyDispersion<TInstance>(
    TInstance instance, int p, float beta, int? seed = null)
    : FastGreedyDispersion<TInstance>(instance, p, seed)
    where TInstance : BaseInstance
{
    private RestrictedCandidateList RestrictedCandidateList { get; } = new(beta, seed);

    /// <summary>
    /// <inheritdoc/>
    /// Populates the restricted candidate list.
    /// </summary>
    /// <remarks><inheritdoc/></remarks>
    protected override void UpdateMemoryInPlace(
        Dictionary<int, int> distancesMemory,
        HashSet<int> closedFacilities,
        int lastInserted)
    {
        // update memory
        // O(m - p) ~= O(m)
        foreach (var fi in closedFacilities)
        {
            distancesMemory[fi] = Math.Min(
                distancesMemory[fi],
                Instance.DistancesFF[fi, lastInserted]);

            RestrictedCandidateList.Add(fi, distancesMemory[fi]);
        }
    }

    /// <summary>
    /// <inheritdoc cref="RestrictedCandidateList.GetFacilityToInsert"/>
    /// </summary>
    /// <remarks>Time O(m)</remarks>
    protected override int GetBestFacilityToInsert(Dictionary<int, int> distancesMemory)
    {
        // O(m)
        return RestrictedCandidateList.GetFacilityToInsert();
    }
}
