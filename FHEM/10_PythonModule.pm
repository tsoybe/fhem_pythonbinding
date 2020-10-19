
# $Id: 10_PythonModule.pm 18283 2019-01-16 16:58:23Z dominikkarall $

package main;

use strict;
use warnings;

use JSON;
use Time::HiRes qw(time);

sub Log($$);
sub Log3($$$);

sub
PythonModule_Initialize($)
{
  my ($hash) = @_;

  $hash->{parseParams} = 1;

  $hash->{DefFn}    = 'PythonModule_Define';
  $hash->{UndefFn}  = 'PythonModule_Undefine';
  $hash->{GetFn}    = 'PythonModule_Get';
  $hash->{SetFn}    = 'PythonModule_Set';
  $hash->{AttrFn}   = 'PythonModule_Attr';
  $hash->{RenameFn} = 'PythonModule_Rename';
  $hash->{AttrList} = 'IODev '.$readingFnAttributes;

  return undef;
}

sub
PythonModule_Define($$$)
{
  my ($hash, $a, $h) = @_;
  $hash->{args} = $a;
  $hash->{argsh} = $h;
  $hash->{PYTHONTYPE} = @$a[2];
  
  # check if BindingsIo exists
  if ($init_done) {
    my $foundServer = 0;
    foreach my $fhem_dev (sort keys %main::defs) {
      if($main::defs{$fhem_dev}{TYPE} eq 'BindingsIo') {
        $foundServer = 1;
      }
    }
    if ($foundServer == 0) {
      return "Before you use PythonModule please define BindingsIo once:\ndefine pyBinding BindingsIo Python";
    }
  }

  Log3 $hash, 3, "PythonModule v1.0.0 (".$hash->{PYTHONTYPE}.")";

  AssignIoPort($hash);

  if (!defined(DevIo_IsOpen($defs{$hash->{IODev}}))) {
    Log3 $hash, 3, "PythonModule: PythonBinding not yet connected! Define after connect...";
    return undef;
  }

  return IOWrite($hash, $hash, "Define", $a, $h);
}

sub
PythonModule_Undefine($$)
{
  my ($hash, $name) = @_;

  IOWrite($hash, $hash, "Undefine", [], {});

  return undef;
}

sub
PythonModule_Get($$$)
{
  my ($hash, $a, $h) = @_;

  return IOWrite($hash, $hash, "Get", $a, $h);
}

sub
PythonModule_Set($$$)
{
  my ($hash, $a, $h) = @_;

  return IOWrite($hash, $hash, "Set", $a, $h);
}

sub
PythonModule_Attr($$$)
{
  my ($cmd, $name, $attrName, $attrVal) = @_;

  return IOWrite($defs{$name}, $defs{$name}, "Attr", [$cmd, $name, $attrName, $attrVal], {});
}

sub
PythonModule_Rename($$$)
{
  my ($oldname, $newname) = @_;

  return IOWrite($defs{$oldname}, $defs{$oldname}, "Rename", [$oldname, $newname], {});
}

sub
PythonModule_ChangeDevIo($)
{
  my ($hash) = $_;
  IOWrite($hash, $hash, "Define", $hash->{args}, $hash->{argsh});
}

sub
PythonModule_DelayedShutdownFn($)
{
  my ($hash) = @_;

  return IOWrite($hash, $hash, "DelayedShutdown", [], {});
}

sub
PythonModule_Shutdown($)
{
  my ($hash) = @_;

  return IOWrite($hash, $hash, "Shutdown", [], {});
}

1;

=pod
=item summary    Interface for Python modules
=item summary_DE Schnittstelle fuer Python Module
=begin html

<a name="PythonModule"></a>
<h3>PythonModule</h3>
<ul>
  This module provides the interface for python modules.<br><br>
  <a href="https://github.com/dominikkarall/fhem_pythonbinding/blob/master/README.md">Click here for online README</a>
</ul><br>

=end html
=cut
