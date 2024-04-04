using Anpcp.Core.Instances;
using Anpcp.Core.Solutions;

namespace Anpcp.Core.Heuristics.Constructives;

/// <summary>
/// Fast Greedy Dispersion (FGD) constructive heuristic.
/// Solves the p-dispersion problem (PDP).
/// </summary>
/// <remarks>
/// This algorithm reduces the time complexity from O(mp**2) to O(mp).
/// </remarks>
public class FgdConstructive(InstanceSameSet instance, int p, int? seed = null)
    : IConstructive<InstanceSameSet, PdpSolution>
{
    public int PSize { get; } = p;
    public InstanceSameSet Instance { get; } = instance;
    public int? Seed { get; } = seed;

    /// <summary>
    /// Greedily constructs a solution for the PDP.
    /// </summary>
    /// <remarks>Time O(mp)</remarks>
    /// <returns>
    /// A solution with updated objective function value in O(1).
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
        var solution = new PdpSolution(Instance.FacilitiesIndices.ToHashSet());

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
        while (solution.OpenFacilities.Count < PSize)
        {
            // update memory
            // O(m - p) ~= O(m)
            foreach (var fi in solution.ClosedFacilities)
            {
                distancesMemory[fi] = Math.Min(
                    distancesMemory[fi],
                    Instance.DistancesFF[fi, lastInserted]);
            }

            // get farthest facility to S
            // O(m - p) ~= O(m)
            lastInserted = distancesMemory
                .MaxBy(p => p.Value)
                .Key;

            solution.Insert(lastInserted);

            // update x(S)
            currentOfv = Math.Min(
                currentOfv,
                distancesMemory[lastInserted]);

            distancesMemory.Remove(lastInserted);
        }

        solution.ObjectiveFunctionValue = currentOfv;

        return solution;
    }
}
