namespace Anpcp.Core.Heuristics.Constructives.Rgd;

/// <summary>
/// Restricted Candidate List (RCL) component for a constructive heuristic within GRASP.
/// </summary>
/// <param name="beta">GRASP parameter.</param>
/// <param name="seed">Seed for random operations.</param>
public class RestrictedCandidateList(float beta, int? seed)
{
    private readonly List<(int FacilityId, int Distance)> _candidates = [];

    private float Beta { get; } = beta;
    private Random Random { get; } = seed is null
        ? new Random()
        : new Random(seed.Value);

    private int MaxCost { get; set; } = int.MinValue;
    private int MinCost { get; set; } = int.MaxValue;
    private float? Threshold { get; set; }

    /// <summary>
    /// Adds a facility to the RCL and updates the maximum and minimum costs,
    /// which will be used to calculate the threshold.
    /// </summary>
    public void Add(int facilityId, int distance)
    {
        _candidates.Add((facilityId, distance));

        MaxCost = Math.Max(MaxCost, distance);
        MinCost = Math.Min(MinCost, distance);
    }

    /// <summary>
    /// Gets at random a facility to insert following the threshold formula
    /// and then clears the list.
    /// </summary>
    /// <returns>ID of the facility to insert.</returns>
    /// <remarks>Time O(m)</remarks>
    public int GetFacilityToInsert()
    {
        Threshold = MaxCost - (Beta * (MaxCost - MinCost));

        // O(m)
        var thresholdedCandidateIds = _candidates
            .Where(c => c.Distance >= Threshold)
            .Select(c => c.FacilityId)
            .ToArray();

        var randomIndex = Random.Next(thresholdedCandidateIds.Length);

        var randomId = thresholdedCandidateIds[randomIndex];

        Clear();

        return randomId;
    }

    /// <summary>
    /// Clears the candidates list and resets the threshold values.
    /// </summary>
    private void Clear()
    {
        _candidates.Clear();

        MaxCost = int.MinValue;
        MinCost = int.MaxValue;
        Threshold = null;
    }
}
