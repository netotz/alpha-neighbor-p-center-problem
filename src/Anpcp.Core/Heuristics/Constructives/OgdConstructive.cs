namespace Anpcp.Core.Heuristics.Constructives;

/// <summary>
/// Original Greedy Dispersion (OGD) constructive heuristic.
/// Solves the p-dispersion problem (PDP).
/// </summary>
public class OgdConstructive(Instance instance, int p, int? seed = null)
    : IConstructive
{
    public int PSize { get; } = p;
    public Instance Instance { get; } = instance;
    public int? Seed { get; } = seed;

    /// <summary>
    /// Greedily constructs a solution for the PDP.
    /// </summary>
    /// <remarks>Time O(mp**2)</remarks>
    public PdpSolution Construct()
    {
        // O(m)
        var solution = new PdpSolution(Instance.FacilitiesIndices.ToHashSet());

        var random = Seed is null
            ? new Random()
            : new Random(Seed.Value);

        // start with random center
        var lastInserted = random.GetItems(
            solution.ClosedFacilities.ToArray(), 1)[0];

        solution.Insert(lastInserted);

        //// O(mp**2)
        // O(p)
        while (solution.OpenFacilities.Count < PSize)
        {
            var distancesToSolution = new Dictionary<int, int>();

            //// O(mp)
            // O(m - p) ~= O(m)
            foreach (var fi in solution.ClosedFacilities)
            {
                // O(p)
                var distance = solution.OpenFacilities
                    .Select(c => Instance.DistancesFF[fi, c])
                    .Min();

                distancesToSolution[fi] = distance;
            }

            // get farthest facility to S
            // O(m - p) ~= O(m)
            lastInserted = distancesToSolution
                .MaxBy(p => p.Value)
                .Key;

            solution.Insert(lastInserted);
        }

        return solution;
    }
}
