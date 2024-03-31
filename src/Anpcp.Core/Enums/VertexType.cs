namespace Anpcp.Core.Enums;

public enum VertexType
{
    User,
    Facility,
    /// <summary>
    /// If there is only one set of nodes,
    /// a vertex can be both a user and a facility.
    /// </summary>
    Both
}
