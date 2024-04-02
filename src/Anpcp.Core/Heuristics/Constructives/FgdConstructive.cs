namespace Anpcp.Core.Heuristics.Constructives;

/// <summary>
/// Fast Greedy Dispersion (FGD) constructive heuristic.
/// Solves the p-dispersion problem (PDP).
/// </summary>
/// <remarks>
/// This algorithm reduces the time complexity from O(mp**2) to O(mp).
/// </remarks>
public class FgdConstructive(Instance instance, int p, int? seed = null)
    : IConstructive
{
    public int PSize { get; } = p;
    public Instance Instance { get; } = instance;
    public int? Seed { get; } = seed;

    /// <summary>
    /// Greedily constructs a solution for the PDP.
    /// </summary>
    /// <remarks>Time O(mp)</remarks>
    public Solution Construct()
    {
        // memory dictionary, O(m)
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
        var solution = new Solution(Instance.FacilitiesIndices.ToHashSet());

        var random = Seed is null
            ? new Random()
            : new Random(Seed.Value);

        var lastInserted = random.GetItems(
            solution.ClosedFacilities.ToArray(), 1)[0];

        solution.Insert(lastInserted);
        distancesMemory.Remove(lastInserted);

        //// O(mp)
        // O(p)
        while (solution.OpenFacilities.Count < PSize)
        {
            // O(m)
            foreach (var fi in solution.ClosedFacilities)
            {
                distancesMemory[fi] = Math.Min(
                    distancesMemory[fi],
                    Instance.DistancesFF[fi, lastInserted]);
            }

            // O(m)
            lastInserted = distancesMemory
                .MaxBy(p => p.Value)
                .Key;

            solution.Insert(lastInserted);
            distancesMemory.Remove(lastInserted);
        }

        return solution;
    }
}
