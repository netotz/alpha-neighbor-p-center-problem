using Anpcp.Core.Heuristics.LocalSearches.Afvs.Models;
using Anpcp.Core.Instances;
using Anpcp.Core.Solutions;
using Anpcp.Core.Solutions.Models;

namespace Anpcp.Core.Heuristics.LocalSearches.Afvs;

/// <summary>
/// Alpha Fast Vertex Substitution (A-FVS) local search heuristic.
/// Improves a solution for the ANPCP.
/// </summary>
public class AlphaFastVertexSubstitution
    : ILocalSearch<InstanceTwoSets, AnpcpSolution>
{
    public int PSize { get; }
    public int Alpha { get; }
    public InstanceTwoSets Instance { get; }
    public int? Seed { get; }
    public AnpcpSolution Solution { get; private set; }

    /// <summary>
    /// Total number of applied moves or swaps.
    /// </summary>
    public int TotalMoves { get; private set; } = 0;
    public Allocator Allocator { get; }

    /// <remarks>Time O(nm)</remarks>
    public AlphaFastVertexSubstitution(
        InstanceTwoSets instance,
        int pSize, int alpha,
        AnpcpSolution startingSolution,
        int? seed = null)
    {
        if (alpha >= pSize)
        {
            throw new ArgumentException(
                $"Parameter `alpha`={alpha} must be strictly less than `p`={pSize}.");
        }

        PSize = pSize;
        Alpha = alpha;
        Instance = instance;
        Seed = seed;

        Allocator = new(alpha, instance.N, instance.M, instance.DistancesUF.IdIndexMap);
        // O(nm)
        SetSolution(startingSolution);
    }

    /// <summary>
    /// Tries to improve <see cref="Solution"/> while counting the <see cref="TotalMoves"/>.
    /// </summary>
    /// <returns>Whether or not the solution got improved at least once.</returns>
    /// <remarks>Time <c>O(nmp)*C</c>, where <c>C</c> is the amount of moves performed.</remarks>
    public bool TryImprove()
    {
        //// O(nmp)*C
        // O(C)
        while (true)
        {
            // O(nmp)
            var bestSwap = GetBestSwap();

            if (bestSwap is null
                // if current x(S) is still less or equal than best swap found
                || Solution.ObjectiveFunctionValue <= bestSwap.ObjectiveFunctionValue)
            {
                // no improvement
                break;
            }

            // O(nm)
            ApplySwap(bestSwap);
            TotalMoves++;
        }

        return TotalMoves > 0;
    }

    /// <summary>
    /// Finds the swap that minimizes x(S) the most.
    /// </summary>
    /// <remarks>Time O(nmp)</remarks>
    private PotentialSwap? GetBestSwap()
    {
        // best x(S) starts as current x(S)
        var bestOfv = Solution.ObjectiveFunctionValue;
        int? bestFi = null;
        int? bestFr = null;

        //// O(nmp)
        // O(m)
        foreach (var facilityIn in Solution.ClosedFacilities)
        {
            if (!DoesBreakCritical(facilityIn))
            {
                // ignore candidates that wouldn't even minimize the current x(S)
                continue;
            }

            // O(np)
            var potentialSwap = GetPotentialSwap(facilityIn);

            // if removing fr improves x(S)
            if (potentialSwap.ObjectiveFunctionValue < bestOfv)
            {
                bestOfv = potentialSwap.ObjectiveFunctionValue;
                bestFi = facilityIn;
                bestFr = potentialSwap.FacilityOut;

                // TODO: break if first improvement
            }
        }

        return bestFi is null || bestFr is null
            // if none of the fi broke critical allocation
            ? null
            : new PotentialSwap(bestFi.Value, bestFr.Value, bestOfv);
    }

    /// <summary>
    /// Finds a potential swap given the candidate <paramref name="facilityIn"/>.
    /// </summary>
    /// <remarks>Time O(np)</remarks>
    private PotentialSwap GetPotentialSwap(int facilityIn)
    {
        // x'
        var bestOfv = int.MinValue;

        // z(.), penalties of removing a center
        // O(p)
        var losses = Solution.Centers
            .ToDictionary(c => c, _ => 0);
        // r(.), gains of keeping a center
        // O(p)
        var gains = losses.ToDictionary();

        //// O(np)
        // O(n)
        foreach (var userId in Instance.UserIds)
        {
            var fiDistance = Instance.DistancesUF[userId, facilityIn];

            // O(p)
            var alphaNeighborhood = new AlphaNeighborhood(
                Alpha, userId, fiDistance,
                Solution.Centers,
                Allocator,
                Instance.DistancesUF);

            var partialLoss = 0;
            var partialGain = 0;

            // if user is attracted to fi
            if (alphaNeighborhood.IsUserAttracted)
            {
                // m_z
                partialLoss = alphaNeighborhood.AlphaDistance;
                // m_r, store the farthest distance between fi and a-1
                partialGain = Math.Max(
                    fiDistance,
                    //! won't work when alpha = 1 (PCP)
                    alphaNeighborhood.AlphaMinusOneDistance);

                bestOfv = Math.Max(bestOfv, partialGain);
            }
            else
            {
                partialLoss = Math.Min(
                    fiDistance,
                    alphaNeighborhood.AlphaPlusOneDistance);
                partialGain = alphaNeighborhood.AlphaDistance;
            }

            // O(a) ~= O(1)
            foreach (var centerId in alphaNeighborhood.GetUpdatingIds())
            {
                losses[centerId] = Math.Max(losses[centerId], partialLoss);
                gains[centerId] = Math.Max(gains[centerId], partialGain);
            }
        }

        // O(p)
        var largestTwoGains = new LargestTwoGains(gains);
        // O(p)
        var (facilityOut, minimumOfv) = GetMinimumOfv(bestOfv, losses, largestTwoGains);

        return new PotentialSwap(facilityIn, facilityOut, minimumOfv);
    }

    /// <summary>
    /// Finds the minimum x(S) among the data structures.
    /// </summary>
    /// <returns>A tuple of the facility to remove and the x(S) it would produce.</returns>
    /// <remarks>Time O(p)</remarks>
    private static (int FacilityOut, int MinimumOfv) GetMinimumOfv(
        int bestOfv,
        Dictionary<int, int> losses,
        LargestTwoGains largestTwoGains)
    {
        var minimumFacilityOut = -1;
        var minimumOfv = int.MaxValue;

        // O(p)
        foreach (var (facilityOut, loss) in losses)
        {
            // TODO: move this inside LargestTwoGains
            var largestGain = facilityOut == largestTwoGains.First.Id
                ? largestTwoGains.Second.ObjectiveFunctionValue
                : largestTwoGains.First.ObjectiveFunctionValue;

            var currentOfv = new[] { bestOfv, loss, largestGain }.Max();

            if (currentOfv < minimumOfv)
            {
                minimumFacilityOut = facilityOut;
                minimumOfv = currentOfv;
            }
        }

        return (minimumFacilityOut, minimumOfv);
    }

    /// <summary>
    /// Checks if <paramref name="facilityIn"/> is nearer to the critical user than
    /// its current alpha-center, i.e., if inserting it would break the critical allocation.
    /// </summary>
    /// <remarks>This is merely a check and does not modify the solution.</remarks>
    private bool DoesBreakCritical(int facilityIn)
    {
        var criticalUser = Solution.CriticalAllocation.UserId;
        var fiDistance = Instance.DistancesUF[criticalUser, facilityIn];

        return fiDistance < Solution.ObjectiveFunctionValue;
    }

    /// <summary>
    /// Modifies the solution by applying <paramref name="bestSwap"/>, updating its state.
    /// </summary>
    /// <remarks>Time O(nm)</remarks>
    private void ApplySwap(PotentialSwap bestSwap)
    {
        Solution.Swap(bestSwap.FacilityIn, bestSwap.FacilityOut);
        // O(nm)
        UpdateSolution();
    }

    /// <summary>
    /// Allocates all users and then updates the critical allocation.
    /// </summary>
    /// <remarks>Time O(nm)</remarks>
    private void UpdateSolution()
    {
        // O(nm)
        Allocator.AllocateAll(
            Instance.UserIds,
            Instance.DistancesUF.GetNextNearestFacility,
            Solution.Centers);

        // O(np)
        Solution.UpdateCriticalAllocation(Instance.UserIds, GetAlphathNearest);
    }

    /// <summary>
    /// Sets <see cref="Solution"/> state to <paramref name="solution"/>
    /// and updates <see cref="Allocator"/>.
    /// </summary>
    /// <remarks>Time O(nm)</remarks>
    /// <exception cref="ArgumentException"></exception>
    public void SetSolution(AnpcpSolution solution)
    {
        if (solution.Size != PSize)
        {
            throw new ArgumentException(
                $"Starting solution must be feasible and contain exactly `p`={PSize} centers.");
        }

        Solution = solution;

        // O(nm)
        UpdateSolution();
    }

    /// <summary>
    /// Gets the alpha-th nearest center of <paramref name="userId"/>.
    /// </summary>
    /// <exception cref="KeyNotFoundException">
    /// Thrown if <paramref name="userId"/> is not allocated.
    /// </exception>
    /// <remarks>Time O(p)</remarks>
    private Allocation GetAlphathNearest(int userId)
    {
        // O(p)
        foreach (var centerId in Solution.Centers)
        {
            var allocatedProximity = Allocator.ById(userId, centerId);

            if (allocatedProximity == Alpha)
            {
                var distance = Instance.DistancesUF[userId, centerId];
                return new(userId, centerId, distance);
            }
        }

        throw new KeyNotFoundException(
            $"User {userId} is missing an allocation to its {Alpha}-th nearest center.");
    }

    /// <summary>
    /// Gets the set of alpha-neighbors of <paramref name="userId"/>.
    /// </summary>
    /// <remarks>Time O(p)</remarks>
    private Dictionary<int, Allocation> GetAlphaNeighbors(int userId)
    {
        var alphaNeighbors = new Dictionary<int, Allocation>();

        // O(p)
        foreach (var centerId in Solution.Centers)
        {
            var proximity = Allocator.ById(userId, centerId);

            // ignore empty allocations
            if (proximity == 0)
            {
                continue;
            }

            var distance = Instance.DistancesUF[userId, centerId];
            alphaNeighbors[proximity] = new(userId, centerId, distance);

            // when all proximities are found
            if (alphaNeighbors.Count == Alpha + 1)
            {
                break;
            }
        }

        return alphaNeighbors;
    }
}
