using Anpcp.Core.Instances;
using Anpcp.Core.Solutions;

namespace Anpcp.Core.Heuristics.Constructives.Rgd;

/// <summary>
/// Randomized Greedy Dispersion (RGD) constructive heuristic to use within GRASP.
/// Solves the p-dispersion problem (PDP).
/// </summary>
public class RandomizedGreedyDispersion<TInstance>(
    TInstance instance,
    int p, float beta,
    int? seed = null)
    : IConstructive<TInstance, AnpcpSolution>
    where TInstance : BaseInstance
{
    public int PSize { get; } = p;
    public TInstance Instance { get; } = instance;
    public int? Seed { get; } = seed;

    private RestrictedCandidateList RestrictedCandidateList { get; } = new(beta, seed);

    /// <summary>
    /// Constructs a solution using PDP's  objective function for GRASP using a RCL.
    /// </summary>
    /// <remarks>Time O(mp)</remarks>
    /// <returns>
    /// A <see cref="AnpcpSolution"/> with no updated objective function value.
    /// </returns>
    public AnpcpSolution Construct()
    {
        // memory dictionary of minimum distances to S
        // O(m)
        var distancesMemory = Enumerable
            .Repeat(int.MaxValue, Instance.Facilities.Length)
            .Select((v, i) => new
            {
                Key = i,
                Value = v
            })
            .ToDictionary(
                s => s.Key,
                s => s.Value);

        // O(m)
        var solution = new AnpcpSolution(Instance.FacilityIds.ToHashSet());

        // current objective function value x(S)
        var currentOfv = int.MaxValue;

        var random = Seed is null
            ? new Random()
            : new Random(Seed.Value);

        // start with random center
        var lastInserted = random.GetItems(
            solution.ClosedFacilities.ToArray(), 1)[0];

        solution.Insert(lastInserted);
        distancesMemory.Remove(lastInserted);

        //// O(mp)
        // O(p)
        while (solution.Size < PSize)
        {
            // O(m)
            UpdateMemoryInPlace(distancesMemory, solution.ClosedFacilities, lastInserted);

            // O(m)
            lastInserted = GetBestFacilityToInsert(distancesMemory);

            solution.Insert(lastInserted);

            // update x(S)
            currentOfv = Math.Min(
                currentOfv,
                distancesMemory[lastInserted]);

            distancesMemory.Remove(lastInserted);
        }

        return solution;
    }

    /// <summary>
    /// Updates <paramref name="distancesMemory"/> in-place (by reference)
    /// and populates the restricted candidate list (RCL).
    /// </summary>
    /// <remarks>Time O(m)</remarks>
    private void UpdateMemoryInPlace(
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

    /// <inheritdoc cref="RestrictedCandidateList.GetFacilityToInsert"/>
    private int GetBestFacilityToInsert(Dictionary<int, int> distancesMemory)
    {
        // O(m)
        return RestrictedCandidateList.GetFacilityToInsert();
    }
}
