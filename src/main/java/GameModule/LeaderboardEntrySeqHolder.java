package GameModule;


/**
* GameModule/LeaderboardEntrySeqHolder.java .
* Generated by the IDL-to-Java compiler (portable), version "3.2"
* from GameService.idl
* Saturday, May 24, 2025 4:33:59 AM SGT
*/

public final class LeaderboardEntrySeqHolder implements org.omg.CORBA.portable.Streamable
{
  public GameModule.LeaderboardEntryDTO value[] = null;

  public LeaderboardEntrySeqHolder ()
  {
  }

  public LeaderboardEntrySeqHolder (GameModule.LeaderboardEntryDTO[] initialValue)
  {
    value = initialValue;
  }

  public void _read (org.omg.CORBA.portable.InputStream i)
  {
    value = GameModule.LeaderboardEntrySeqHelper.read (i);
  }

  public void _write (org.omg.CORBA.portable.OutputStream o)
  {
    GameModule.LeaderboardEntrySeqHelper.write (o, value);
  }

  public org.omg.CORBA.TypeCode _type ()
  {
    return GameModule.LeaderboardEntrySeqHelper.type ();
  }

}
