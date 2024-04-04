﻿namespace Anpcp.Core;

public class PdpSolution(HashSet<int> closedFacilities)
    : BaseSolution(closedFacilities)
{
    /// <summary>
    /// <inheritdoc/>
    /// Finds the minimum distance among all pairs of centers.
    /// </summary>
    /// <remarks>Time O(p**2)</remarks>
    public override int UpdateObjectiveFunctionValue(Instance instance)
    {
        // O(p)
        var openFacilitiesArray = OpenFacilities.ToArray();

        var minDistance = 0;

        //// O(p)
        // O(p)
        for (var i = 0; i < openFacilitiesArray.Length; i++)
        {
            var center1 = openFacilitiesArray[i];
            // O(p)
            for (var j = i + 1; j < openFacilitiesArray.Length; j++)
            {
                var center2 = openFacilitiesArray[j];

                var distance = instance.DistancesFF[center1, center2];
                minDistance = Math.Min(minDistance, distance);
            }
        }

        ObjectiveFunctionValue = minDistance;

        return minDistance;
    }
}
