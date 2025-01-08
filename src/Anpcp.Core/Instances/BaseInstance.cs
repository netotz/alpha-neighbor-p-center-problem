using System.Collections.Immutable;

using Anpcp.Core.Models;
using Anpcp.Core.Wrappers;

namespace Anpcp.Core.Instances;

public abstract class BaseInstance
{
    public string Name { get; protected set; } = "";
    public Vertex[] Facilities { get; protected set; } = [];
    /// <summary>
    /// Total number of facilities.
    /// </summary>
    /// <remarks><c>m = |F|</c></remarks>
    public int M => Facilities.Length;
    /// <summary>
    /// Set of facility IDs.
    /// </summary>
    public ImmutableHashSet<int> FacilityIds { get; private set; } = [];
    public Vertex[] Users { get; protected set; } = [];
    /// <summary>
    /// Total number of users.
    /// </summary>
    /// <remarks><c>n = |U|</c></remarks>
    public int N => Users.Length;
    /// <summary>
    /// Set of user IDs.
    /// </summary>
    public ImmutableHashSet<int> UserIds { get; private set; } = [];
    /// <summary>
    /// Matrix of distances between users and facilities.
    /// </summary>
    public DistancesMatrix DistancesUF { get; protected set; } = new();
    /// <summary>
    /// Matrix of distances between facilities.
    /// </summary>
    public DistancesMatrix DistancesFF { get; protected set; } = new();

    protected void InitializeSets()
    {
        if (M == 0)
        {
            throw new InvalidOperationException(
                "Array of vertex facilities is empty. Cannot create set.");
        }

        FacilityIds = Facilities
            .Select(f => f.Id)
            .ToImmutableHashSet();

        if (N == 0)
        {
            throw new InvalidOperationException(
                "Array of vertex users is empty. Cannot create set.");
        }

        UserIds = Users
            .Select(u => u.Id)
            .ToImmutableHashSet();
    }
}
