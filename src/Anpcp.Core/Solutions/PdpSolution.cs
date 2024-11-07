﻿using Anpcp.Core.Wrappers;

namespace Anpcp.Core.Solutions;

public class PdpSolution(HashSet<int> closedFacilities)
    : BaseSolution(closedFacilities)
{
    /// <summary>
    /// Indices pair of critical vertices whose distance
    /// defines <see cref="ObjectiveFunctionValue"/>.
    /// </summary>
    public (int, int) CriticalPair { get; protected set; } = (-1, -1);

    /// <summary>
    /// <inheritdoc/>
    /// Finds the minimum distance among all pairs of centers.
    /// </summary>
    /// <param name="distancesFF">Distances matrix of facilities.</param>
    /// <remarks>Time O(p**2)</remarks>
    public override int UpdateObjectiveFunctionValue(DistancesMatrix distancesFF)
    {
        // O(p)
        var openFacilitiesArray = OpenFacilities.ToArray();

        var minDistance = int.MaxValue;

        //// O(p**2)
        // O(p)
        for (var i = 0; i < openFacilitiesArray.Length; i++)
        {
            var center1 = openFacilitiesArray[i];
            // O(p)
            for (var j = i + 1; j < openFacilitiesArray.Length; j++)
            {
                var center2 = openFacilitiesArray[j];

                var distance = distancesFF[center1, center2];

                if (distance < minDistance)
                {
                    minDistance = distance;
                    CriticalPair = (center1, center2);
                }
            }
        }

        ObjectiveFunctionValue = minDistance;

        return minDistance;
    }
}
