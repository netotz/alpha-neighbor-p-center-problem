using Anpcp.Core.Instances;
using Anpcp.Core.Solutions;

namespace Anpcp.Core.Heuristics.Constructives;

/// <summary>
/// Fast Greedy Dispersion (FGD) constructive heuristic.
/// Solves the p-dispersion problem (PDP).
/// </summary>
/// <remarks>
/// This algorithm reduces the time complexity from O(mp**2) to O(mp)
/// and gets the objective function value of the PDP in O(1).
/// </remarks>
public class FastGreedyDispersion<TInstance>(
    TInstance instance,
    int p,
    int? seed = null)
    : IConstructive<TInstance, PdpSolution>
    where TInstance : BaseInstance
{
    public int PSize { get; } = p;
    public TInstance Instance { get; } = instance;
    public int? Seed { get; } = seed;

    /// <summary>
    /// Greedily constructs a solution for the PDP.
    /// </summary>
    /// <remarks>Time O(mp)</remarks>
    /// <returns>
    /// A <see cref="PdpSolution"/> with updated objective function value in O(1).
    /// </returns>
    public PdpSolution Construct()
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
        var solution = new PdpSolution(Instance.FacilityIds.ToHashSet());

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

        // TODO: add corresponding center in distances memory to get actual critical pair
        solution.UpdateCriticalAllocation(-1, -1, currentOfv);

        return solution;
    }

    /// <summary>
    /// Updates <paramref name="distancesMemory"/> in-place (by reference).
    /// </summary>
    /// <remarks>Time O(m)</remarks>
    protected virtual void UpdateMemoryInPlace(
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
        }
    }

    /// <summary>
    /// Gets the best facility to insert by getting the argument of
    /// the maximum value in <paramref name="distancesMemory"/>.
    /// </summary>
    /// <returns>ID of the best facility to insert.</returns>
    /// <remarks>Time O(m)</remarks>
    protected virtual int GetBestFacilityToInsert(Dictionary<int, int> distancesMemory)
    {
        // get farthest facility to S
        // O(m - p) ~= O(m)
        return distancesMemory
            .MaxBy(p => p.Value)
            .Key;
    }
}
